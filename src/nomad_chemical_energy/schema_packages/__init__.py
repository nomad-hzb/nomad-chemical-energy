from nomad.config.models.plugins import SchemaPackageEntryPoint


class CEAMCCPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.ce_amcc_package import m_package

        return m_package


class CENOMEPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.ce_nome_package import m_package

        return m_package


class CENECCPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.ce_necc_package import m_package

        return m_package


class CEACMDPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.ce_nesd_package import m_package

        return m_package


class CENSLIPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.ce_nsli_package import m_package

        return m_package


class CEWannseePackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.ce_wannsee_package import m_package

        return m_package


class HZBCharacterizationPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.hzb_characterization_package import (
            m_package,
        )

        return m_package


class HZBCatlabPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.hzb_catlab_package import m_package

        return m_package


class DLRECPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.dlr_electro_chemistry_package import (
            m_package,
        )

        return m_package


class HZBGeneralPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.hzb_general_process_package import (
            m_package,
        )

        return m_package


class TFCPackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.tfc_package import (
            m_package,
        )

        return m_package


class PublicShowcasePackageEntryPoint(SchemaPackageEntryPoint):
    def load(self):
        from nomad_chemical_energy.schema_packages.public_showcase_package import (
            m_package,
        )

        return m_package


ce_amcc_package = CEAMCCPackageEntryPoint(
    name='CE_AMCC',
    description='Package for HZB group CE-AMCC',
)

ce_nome_package = CENOMEPackageEntryPoint(
    name='CE_NOME',
    description='Package for HZB group CE-NOME',
)

ce_necc_package = CENECCPackageEntryPoint(
    name='CE_NECC',
    description='Package for HZB group CE-NECC',
)

ce_acmd_package = CEACMDPackageEntryPoint(
    name='CE_ACMD',
    description='Package for HZB group CE-ACMD',
)

ce_nsli_package = CENSLIPackageEntryPoint(
    name='CE_NSLI',
    description='Package for HZB group CE-NSLI',
)

ce_wannsee_package = CEWannseePackageEntryPoint(
    name='CE_Wannsee',
    description='Package for HZB general CE at Wannsee',
)

hzb_characterization_package = HZBCharacterizationPackageEntryPoint(
    name='HZB_Characterization',
    description='Package for HZB Characterizations',
)


hzb_catlab_package = HZBCatlabPackageEntryPoint(
    name='HZBCatlab',
    description='Package for HZB Catlab Schemas',
)

dlr_ec_package = DLRECPackageEntryPoint(
    name='DLREC',
    description='Package for DLR EC Schemas',
)

hzb_general_process_package = HZBGeneralPackageEntryPoint(
    name='HZBGeneral',
    description='Package for general HZB Schema',
)

tfc_schema_package = TFCPackageEntryPoint(
    name='TFC',
    description='Package for Thin Film Catalysts Group',
)

public_showcase_package = PublicShowcasePackageEntryPoint(
    name='PublicShowcase',
    description='Package for Science Communication at public events like GirlsDay or Long Night of Science',
)
