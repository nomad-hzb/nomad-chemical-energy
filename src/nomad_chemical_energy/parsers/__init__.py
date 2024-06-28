from nomad.config.models.plugins import ParserEntryPoint


class CENECCxlsxParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.ce_necc_parser import NECCXlsxParser
        return NECCXlsxParser(**self.dict())


class CENOMEGamryParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import GamryParser
        return GamryParser(**self.dict())


class CENOMEcsvParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import CENOMEcsvParser
        return CENOMEcsvParser(**self.dict())


class CENOMEUVvisParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import UVvisParser
        return UVvisParser(**self.dict())


class CENOMEXASParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import XASParser
        return XASParser(**self.dict())


class CENOMETIFParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import CENOMETIFParser
        return CENOMETIFParser(**self.dict())


class CEWannseeMPTParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.ce_wannsee_parser import MPTParser
        return MPTParser(**self.dict())


class CEWannseeCORParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.ce_wannsee_parser import CORParser
        return CORParser(**self.dict())


class CEWannseeXRDParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.ce_wannsee_parser import XRDParser
        return XRDParser(**self.dict())


class DLRECCPParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.dlr_electro_chemistry_parser import DLRECCPParser
        return DLRECCPParser(**self.dict())


class DLRECCVParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.dlr_electro_chemistry_parser import DLRECCVParser
        return DLRECCVParser(**self.dict())


class DLRECEISParserEntryPoint(ParserEntryPoint):

    def load(self):
        from nomad_chemical_energy.parsers.dlr_electro_chemistry_parser import DLRECEISParser
        return DLRECEISParser(**self.dict())


ce_necc_xlsx_parser = CENECCxlsxParserEntryPoint(
    name='CENECCxlsxParser',
    description='Parser for CENECC xls files',
    mainfile_name_re='^.*\.xlsx$',
    mainfile_mime_re='(application|text)/.*'
)

ce_nome_gamry_parser = CENOMEGamryParserEntryPoint(
    name='CENOMEGamryParser',
    description='Parser for CENOME Gamry files',
    mainfile_name_re='^(.*\.DTA)$'
)

ce_nome_csv_parser = CENOMEcsvParserEntryPoint(
    name='CENOMEcsvParser',
    description='Parser for CENOME csv files',
    mainfile_name_re='^(.+\.(pump|oxy)\.(csv|xlsx))$',
    mainfile_mime_re='(application|text)/.*'
)

ce_nome_uvvis_parser = CENOMEUVvisParserEntryPoint(
    name='CENOMEUVvisParser',
    description='Parser for CENOME uvvis files',
    mainfile_name_re='^(.*\.(csv|ABS))$',
    mainfile_contents_re='^(.*)(\r\n|\r|\n)((WL\/nm,Abs)|("  ABSOR->  Wave:.*))'
)

ce_nome_xas_parser = CENOMEXASParserEntryPoint(
    name='CENOMEXASParser',
    description='Parser for CENOME xas kmc2 files',
    mainfile_name_re='^(.*(\.dat))',
    mainfile_contents_re='/home/kmc2/data/'
)

ce_nome_tif_parser = CENOMETIFParserEntryPoint(
    name='CENOMETIFParser',
    description='Parser for CENOME tif files',
    mainfile_name_re='^(.*(\.tif|\.tiff))',
    mainfile_mime_re='image/.*'
)


ce_wannsee_mpt_parser = CEWannseeMPTParserEntryPoint(
    name='CEWannseeMPTParser',
    description='Parser for Wannsee mpt files',
    mainfile_name_re='^.*\.mpt$'
)

ce_wannsee_cor_parser = CEWannseeCORParserEntryPoint(
    name='CEWannseeCORParser',
    description='Parser for Wannsee cor files',
    mainfile_name_re='^.*\.cor$'
)

ce_wannsee_xrd_xy_parser = CEWannseeXRDParserEntryPoint(
    name='CEWannseeXRDParser',
    description='Parser for Wannsee xy xrd files',
    mainfile_name_re='^(.+\.?.+.xy)$'
)


dlr_ec_cv_parser = DLRECCVParserEntryPoint(
    name='DLRECCVParser',
    description='Parser for DLR CV files',
    mainfile_contents_re='^.*\nPotential\sapplied\s\(V\)\tTime\s\(s\)\tWE\(1\).Current\s\(A\)\tScan\tIndex'
)

dlr_ec_cp_parser = DLRECCPParserEntryPoint(
    name='DLRECCPParser',
    description='Parser for DLR CP files',
    mainfile_contents_re='^(.*)\nTime\s\(s\)\tWE\(1\).Potential\s\(V\)\tCorrected\stime\s\(s\)\tIndex'
)

dlr_ec_eis_parser = DLRECEISParserEntryPoint(
    name='DLRECEISParser',
    description='Parser for DLR EIS files',
    mainfile_contents_re='''^.*\nIndex\tFrequency\s\(Hz\)\tZ'\s\(Ω\)\s-Z''\s\(Ω\)\tZ\s\(Ω\)\s-Phase\s\(°\)\tTime\s\(s\)'''
)
