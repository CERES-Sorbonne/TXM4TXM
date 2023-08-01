import xmltodict

from transformers.default import DefaultTransformer


class XMLTransformer(DefaultTransformer):

    def transform(self, pivot: dict) -> str:
        pivot = self.epurer(pivot)
        return xmltodict.unparse(pivot, pretty=True)
