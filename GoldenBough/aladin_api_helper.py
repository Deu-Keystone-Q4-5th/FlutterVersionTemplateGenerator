import requests

import Config


class AladinItemListFinder:
    def __init__(self):
        self.url = f"http://www.aladin.co.kr/ttb/api/ItemList.aspx?ttbkey={Config.configManager.config.secret_key}&QueryType=BlogBest&Version=20131101&SearchTarget=Book&MaxResults=10&start=1"
        self.is_json = True
        self.will_filter_sold_out = False
        self.year=-1
        self.month=-1
        self.week=-1


    def set_xml(self, value: bool):
        self.is_json = value
        return self

    def filter_sold_out(self, value: bool):
        self.will_filter_sold_out = value
        return self

    def specific_date(self, year: int, month : int, week : int):
        self.year = year
        self.month = month
        self.week = week

        return self



    def combine_settings(self):
        args = [self.url]
        args.append("&Output=js" if not self.is_json else "&Output=xml")
        if self.year != -1:
            args.append(f"&Year={self.year}")
        if self.month != -1:
            args.append(f"&Month={self.month}")
        if self.week != -1:
            args.append(f"&Week={self.week}")

        if (self.will_filter_sold_out) :
            args.append(f"&outStockfilter=1")
        self.url = "".join(args)
        print("".join(args))

test = AladinItemListFinder()
test.set_xml(True).filter_sold_out(True).combine_settings()