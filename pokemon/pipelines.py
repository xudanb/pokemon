from itemadapter import ItemAdapter

class PokemonPipeline(object):
    # not enabled! maybe useful for database export, etc.
    def process_item(self, item, spider):
        return item