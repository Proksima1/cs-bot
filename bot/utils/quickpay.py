import asyncio

import aiohttp


class Quickpay:
    def __init__(self,
                 receiver: str,
                 quickpay_form: str,
                 targets: str,
                 paymentType: str,
                 sum: float,
                 formcomment: str = None,
                 short_dest: str = None,
                 label: str = None,
                 comment: str = None,
                 successURL: str = None,
                 need_fio: bool = None,
                 need_email: bool = None,
                 need_phone: bool = None,
                 need_address: bool = None,
                 ):
        self.receiver = receiver
        self.quickpay_form = quickpay_form
        self.targets = targets
        self.paymentType = paymentType
        self.sum = sum
        self.formcomment = formcomment
        self.short_dest = short_dest
        self.label = label
        self.comment = comment
        self.successURL = successURL
        self.need_fio = need_fio
        self.need_email = need_email
        self.need_phone = need_phone
        self.need_address = need_address

        self.response = None

    async def __aenter__(self):
        self.response = await self._request()
        return self

    async def __aexit__(self, exc_type, exc, tb):
        pass

    async def _request(self):

        self.base_url = "https://yoomoney.ru/quickpay/confirm.xml?"

        payload = {"receiver": self.receiver, "quickpay_form": self.quickpay_form, "targets": self.targets,
                   "paymentType": self.paymentType, "sum": self.sum}

        if self.formcomment is not None:
            payload["formcomment"] = self.formcomment
        if self.short_dest is not None:
            payload["short_dest"] = self.short_dest
        if self.label is not None:
            payload["label"] = self.label
        if self.comment is not None:
            payload["comment"] = self.comment
        if self.successURL is not None:
            payload["successURL"] = self.successURL
        if self.need_fio is not None:
            payload["need_fio"] = self.need_fio
        if self.need_email is not None:
            payload["need_email"] = self.need_email
        if self.need_phone is not None:
            payload["need_phone"] = self.need_phone
        if self.need_address is not None:
            payload["need_address"] = self.need_address

        for value in payload:
            self.base_url += str(value).replace("_", "-") + "=" + str(payload[value])
            self.base_url += "&"

        self.base_url = self.base_url[:-1].replace(" ", "%20")

        # response = requests.request("POST", self.base_url)
        async with aiohttp.ClientSession(loop=asyncio.get_event_loop()) as client:
            response = await client.post(self.base_url)

        self.redirected_url = str(response.url)
        return
