import re
import scrapy
from scrapy.loader import ItemLoader
from ..items import EquaItem
from itemloaders.processors import TakeFirst
pattern = r'(\xa0)?'

class EquaSpider(scrapy.Spider):
	name = 'equa'
	start_urls = ['https://www.equabank.cz/en/about-us/press-release']

	def parse(self, response):
		post_links = response.xpath('//h3/a/@href').getall()
		yield from response.follow_all(post_links, self.parse_post)

		next_page = response.xpath('//a[@class="btn-group__btn btn-group__btn--paging btn-group__btn--single"]/@href | //a[@class="btn-group__btn btn-group__btn--paging btn-group__btn--last"]/@href').get()
		if next_page:
			yield response.follow(next_page, self.parse)


	def parse_post(self, response):

		date = response.xpath('//div[@class="news__detail-date"]/text()').get()
		date = ''.join([el.strip() for el in date if el.strip()])
		title = response.xpath('//h2[@class="news__detail-title"]/text()').get()
		content = response.xpath('//div[@class="news__detail"]//text()[not (ancestor::div[@class="news__detail-date"]) and not (ancestor::h2[@class="news__detail-title"])]').getall()
		content = [p.strip() for p in content if p.strip()]
		content = re.sub(pattern, "",' '.join(content))


		item = ItemLoader(item=EquaItem(), response=response)
		item.default_output_processor = TakeFirst()

		item.add_value('title', title)
		item.add_value('link', response.url)
		item.add_value('content', content)
		item.add_value('date', date)

		yield item.load_item()
