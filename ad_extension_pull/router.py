class AdExtensionRouter:
    def db_for_read(self, model, **hints):
        """Point all operations on ad_extension_pull models to 'ad_extension'"""
        if model._meta.app_label == 'ad_extension_pull':
            return 'ad_extension'
        return 'default'

    def db_for_write(self, model, **hints):
        """Point all operations on ad_extension_pull models to 'ad_extension'"""
        if model._meta.app_label == 'ad_extension_pull':
            return 'ad_extension'
        return 'default'

    def allow_relation(self, obj1, obj2, **hints):
        """Allow any relation if a both models in ad_extension_pull app"""
        if obj1._meta.app_label == 'ad_extension_pull' and obj2._meta.app_label == 'ad_extension_pull':
            return True
        # Allow if neither is ad_extension_pull app
        elif 'ad_extension_pull' not in [obj1._meta.app_label, obj2._meta.app_label]:
            return True
        return False

    def allow_syncdb(self, db, model):
        if db == 'ad_extension' or model._meta.app_label == "ad_extension_pull":
            return False  # we're not using syncdb on our legacy database
        else:  # but all other models/databases are fine
            return True
