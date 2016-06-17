import scrapy
from edmwer2.items import EdmwerThread as Thread
from edmwer2.items import EdmwerUser as User
from edmwer2.items import EdmwerPost as Post
from edmwer2.items import EdmwerImage as Image
import datetime
import re
import json

class EdmwSpider(scrapy.Spider):
    name = "edmw"
    allowed_domains = ["hardwarezone.com.sg"]
    start_urls = [
        "http://forums.hardwarezone.com.sg/eat-drink-man-woman-16/",
    ]

    def parse(self, response):
        path = "http://forums.hardwarezone.com.sg"
    	threads = response.xpath(
			'//tbody[@id="threadbits_forum_16"]/tr[not(@class="hwz-sticky")]'
		)
        for thread in threads:
            url = thread.xpath(
                'td[@class="alt2"]/div/a[contains(@href,"html#post")]/@href'
            ).extract_first()
            url_elems = url.split('#')
            # add domain
            new_url = path + url_elems[0] 
            
            yield scrapy.Request(new_url, callback=self.parse_threads)

    def parse_threads(self, response):
        # get the item classes
        the_thread = Thread()
        # thread level data
        thread_title = response.selector.xpath('//div[contains(@id,"forum")]/' +
            'h2[@class="header-gray"]/text()').extract_first().strip()
        thread_url = response.url
        thread_url = re.sub('-\d{1,3}\.html$','.html', response.url)
        the_thread['title'] = thread_title
        the_thread['url'] = thread_url
        the_thread['_id'] = \
            int(re.findall('\d+\.html',thread_url)[0].split('.')[0])
        the_thread['ts'] = response.xpath(
            '//a[@class="bigusername"]/text()'
        ).extract_first()
        the_thread['replies'] = \
            int(response.xpath('//a/strong/text()').extract()[-1]) - 1
        yield the_thread

        # prepare posts for second-level crawl
        posts = response.xpath(
            '//div/div[contains(@id,"edit")]/table[contains(@id,"post")]'
        )
        for post in posts:
            the_post = Post()
            the_user = User()
            post_date = post.xpath('./descendant::td/text()[contains(.,AM) ' +
                'or contains(.,PM)]').extract()[2].strip().split(",")
            time = post_date[1].split(" ")
            if time[2] == "AM":
                post_time = time[1]
                timesplit = time[1].split(":")
                if int(timesplit[0]) == 12:
                    post_time = "00:" + str(timesplit[1])
            elif time[2] == "PM":
                timesplit = time[1].split(":")
                if int(timesplit[0]) == 12:
                    post_time = "12:" + str(timesplit[1])
                else:
                    post_time = str(int(timesplit[0])+12) + ":" + \
                        str(timesplit[1])
            if post_date[0] == "Yesterday":
                date_part=str(datetime.date.today() - datetime.timedelta(1))
            elif post_date[0] == "Today":
                date_part=str(datetime.date.today())
            else:
                xx=post_date[0].split("-")
                date_part=xx[2]+"-"+xx[1]+"-"+xx[0]
            post_datetime = datetime.datetime.strptime(
                date_part + " " + post_time, "%Y-%m-%d %H:%M"
            )
            post_user = post.xpath(
                './descendant::a[contains(@class,"bigusername")]/text()'
            ).extract()[0]
            user_url = post.xpath(
                './descendant::a[contains(@class,"bigusername")]/@href'
            ).extract()[0]
            user_status = post.xpath(
                './descendant::td/div[contains(text(),"Member") or ' +
                'contains(text(),"Partner") or contains(text(),"Jedi") or ' +
                'contains(text(),"Trooper") or contains(text(),"Pilot") or ' +
                'contains(text(),"Clone") or contains(text(),"Banned") or ' +
                'contains(text(),"Administrator") or contains(text(),"EDMW") ' +
                'or contains(text(),"Moderator")]/text()'
            ).extract()[0]
            post_count = post.xpath(
                './descendant::div[contains(text(),"Posts:")]/text()'
            ).extract()[0]
            post_count = int(re.sub("[^\d.]+","",post_count))
            join_date = post.xpath(
                './descendant::div[contains(text(),"Join Date:")]/text()'
            ).extract()[0]
            post_id2 = post.xpath(
                './descendant::a[contains(@id,"post")]/@id'
            ).extract()
            post_id = post.xpath(
                './descendant::a[contains(@id,"post")]/@id'
            ).extract()[0]
            post_id = int(re.findall('\d+', post_id)[0])
            post_content = post.xpath(
                './descendant::div[contains(@id,"post_message")]/node()'
            ).extract()

            if post_content:
                post_content = json.dumps(post_content)
            post_quoted = post.xpath(
                './descendant::div[contains(@id,"post_message")]/' +
                'div[@class="quote"]/span/strong/text()'
            ).extract()
            if post_quoted:
                post_quoted = json.dumps(post_quoted)
            post_images = post.xpath(
                './descendant::div[contains(@id,"post_message")]/a/img/' +
                '@src|//div[contains(@id,"post_message")]/a/div/img/' +
                '@src|./descendant::div[contains(@id,"post_message")]/div/' +
                'blockquote/descendant::a/img/@src|./descendant::' +
                'div[contains(@id,"post_message")]/div/a/div/img/@src'
            ).extract()
            if post_images:
                for image in post_images:
                    the_image = Image()
                    the_image['image_url']=image
                    the_image['_id']=post_id
                    yield the_image
                post_images = json.dumps(post_images)
 
            likebox = post.xpath(
                'count(./descendant::div[contains(@class,"vbseo_liked")]' +
                '/a[contains(@href,"users")])'
            ).extract()[0]
            extralikes = post.xpath(
                './descendant::div[contains(@class,"vbseo_liked")]' +
                '/a[contains(text(),"others")]/text()'
            ).extract()
            morelikes = 0
            if extralikes:
                morelikes=int(extralikes[0].split(" ")[0])
            likebox = int(float(likebox))
            post_likes = likebox + morelikes
           
            # post meta 
            the_post["url"]=thread_url
            the_post["title"]=thread_title
            the_post["date"]=post_datetime
            the_post["poster"]=post_user
            the_post["_id"]=post_id
            the_post["content"]=post_content
            the_post["quoted"]=post_quoted
            the_post["likes"]=post_likes
            the_post["image_urls"]=post_images
            yield the_post

            # user meta
            the_user['last_post']=post_id
            the_user['user']=post_user
            the_user['_id']=user_url.split('/')[2] 
            the_user["post_count"]=post_count
            the_user["rank"]=user_status
            the_user["join_date"]=join_date.split(': ')[1]
            yield the_user
