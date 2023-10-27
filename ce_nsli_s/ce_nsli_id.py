from typing import TYPE_CHECKING, Iterable
import datetime
import re
from typing import (
    Dict,
    List,
)

import numpy as np
from ase.data import (
    chemical_symbols,
    atomic_numbers,
    atomic_masses,
)
import requests

from nomad.datamodel.metainfo.workflow import Link, Task, TaskReference, Workflow
if TYPE_CHECKING:
    from structlog.stdlib import (
        BoundLogger,
    )
from nomad.atomutils import (
    Formula,
)
from nomad import (
    utils,
)
from nomad.units import (
    ureg,
)
from nomad.metainfo import (
    Quantity,
    Datetime,
    Reference,
    Section,
    SubSection,
)
from nomad.metainfo.util import (
    MEnum,
)
from nomad.datamodel.data import (
    ArchiveSection,
    EntryData,
)
from nomad.datamodel.results import (
    Results,
    ELN,
    ElementalComposition as ResultsElementalComposition,
    Material,
)
from nomad.datamodel.metainfo.annotations import (
    ELNAnnotation,
)


class CENSLIIdentifier(ArchiveSection):

    owner = Quantity(
        type=str,
        shape=[],
        description='''
        Alias for the owner of the identified thing. This should be unique within the
        institute.
        ''',
        a_eln=dict(component='StringEditQuantity'),
    )
    datetime = Quantity(
        type=Datetime,
        description='''
        A datetime associated with the identified thing. In case of an `Activity`, this
        should be the starting time and, in case of an `Entity`, the creation time.
        ''',
        a_eln=dict(component='DateTimeEditQuantity'),
    )

    mxene_formula = Quantity(
        type=str,
        description='''
        A short name of the the identified thing (e.g. the identifier scribed on the
        sample, the process number, or machine name), e.g. 4001-8, YAG-2-34.
        This is to be managed and decided internally by the labs, although we recommend
        to avoid the following characters in it: "_", "/", "\\" and ".".
        ''',
        a_eln=dict(component='StringEditQuantity'),
    )

    method = Quantity(
        type=MEnum('MS', 'HF'),
        shape=[],
        a_eln=dict(
            component='EnumEditQuantity',
        ))

    lab_id = Quantity(
        type=str,
        description='''
        Full readable id. Ideally a human readable id convention, which is simple,
        understandable and still have chances of becoming unique.
        If the `owner`, `short_name`, `ìnstitute`, and `datetime` are provided, this will
        be formed automatically by joining these components by an underscore (_).
        Spaces in any of the individual components will be replaced with hyphens (-).
        An example would be hzb_oah_20200602_4001-08.
        ''',
        a_eln=dict(component='StringEditQuantity'),
    )

    def normalize(self, archive, logger: 'BoundLogger') -> None:
        '''
        The normalizer for the `ReadableIdentifiers` class.
        If owner is not filled the field will be filled by the first two letters of
        the first name joined with the first two letters of the last name of the author.
        If the institute is not filled a institute abreviations will be constructed from
        the author's affiliation.
        If no datetime is filled, the datetime will be taken from the `datetime`
        property of the parent, if it exists, otherwise the current date and time will be
        used.
        If no short name is filled, the name will be taken from the parent name, if it
        exists, otherwise it will be taken from the archive metadata entry name, if it
        exists, and finally if no other options are available it will use the name of the
        mainfile.

        Args:
            archive (EntryArchive): The archive containing the section that is being
            normalized.
            logger ('BoundLogger'): A structlog logger.
        '''

        if self.owner is None:
            from unidecode import unidecode
            author = archive.metadata.main_author
            if author and self.owner is None:
                first_short = unidecode(author.first_name)[:1]
                last_short = unidecode(author.last_name)[:1]
                self.owner = first_short + last_short

        if self.datetime is None:
            if self.m_parent and getattr(self.m_parent, 'datetime', None):
                self.datetime = self.m_parent.datetime
            else:
                self.datetime = datetime.datetime.now()

        if self.mxene_formula and self.owner and self.datetime and self.mxene_formula and self.method:
            creation_date = self.datetime.strftime('%Y%m%d')
            owner = self.owner.replace(' ', '-')
            lab_id_list = [creation_date, owner, self.mxene_formula, self.method]
            self.lab_id = '_'.join(lab_id_list)

        if not archive.results:
            archive.results = Results(eln=ELN())
        if not archive.results.eln:
            archive.results.eln = ELN()

        if self.lab_id:
            archive.results.eln.lab_ids = [self.lab_id]
