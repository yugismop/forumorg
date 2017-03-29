from flask_admin.contrib.pymongo.filters import BasePyMongoFilter, FilterEqual


class FilterRegister(FilterEqual, BasePyMongoFilter):

    def apply(self, query, value):
        if value == 'ambassador':
            query.append({'events.fra.ambassador': {'$gt': {}}})
        else:
            query.append({'events.{}.registered'.format(value): True})
        return query

    def operation(self):
        return "participe a"


class FilterField(FilterEqual, BasePyMongoFilter):

    def apply(self, query, value):
        if self.column in ['validated', 'delivered', 'denied']:
            value = (value == 'oui')
        if self.column == 'duration':
            query.append({'$or': [{self.column: value}, {self.column: 'both'}]})
            return query
        query.append({self.column: value})
        return query

    def operation(self):
        return "egal a"
