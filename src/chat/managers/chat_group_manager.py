from django.db.models import Manager, QuerySet, Q


class ChatGroupQuerySet(QuerySet):
    pass


class ChatGroupManager(Manager):

    def get_queryset(self):
        return ChatGroupQuerySet(self.model, using=self._db) #Important
