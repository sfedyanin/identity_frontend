import os
import logging

from django.db import models
from django.conf import settings
from django.db import transaction

from django_fsm import TransitionNotAllowed
from django_fsm import FSMFieldMixin, GET_STATE, RETURN_VALUE
from django_fsm import ConcurrentTransition
logger = logging.getLogger('vdx_id.%s' % __name__)


class ViStateGraphEngine(models.Model):
    processing = models.BooleanField(default=True)

    class Meta:
        abstract = True

    @property
    def state(self):
        raise NotImplementedError("Field 'state' not defined")

    @property
    def target_state(self):
        raise NotImplementedError("Field 'target_state' not defined")

    @property
    def cached_network_key(self):
        return 'state_graph_%s' % self.__hash__

    @property
    def data_dir(self):
        path = os.path.join(settings.DATA_DIR, self.data_foldername)
        if not os.path.exists(path):
            os.mkdir(path)
        return path
