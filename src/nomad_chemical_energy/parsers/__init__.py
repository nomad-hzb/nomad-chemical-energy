from nomad.config.models.plugins import ParserEntryPoint


class CEAMCCBioLogicParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_amcc_parser import CEAMCCBioLogicParser

        return CEAMCCBioLogicParser(**self.dict())


class CENECCxlsxParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_necc_parser import NECCXlsxParser

        return NECCXlsxParser(**self.dict())


class CENECCBioLogicParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_necc_parser import CENECCBioLogicParser

        return CENECCBioLogicParser(**self.dict())


class CENESDBioLogicParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nesd_parser import CENESDBioLogicParser

        return CENESDBioLogicParser(**self.dict())


class CENESDZahnerParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nesd_parser import CENESDZahnerParser

        return CENESDZahnerParser(**self.dict())


class CENESDLabviewParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nesd_parser import CENESDLabviewParser

        return CENESDLabviewParser(**self.dict())


class CENESDPalmSensParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nesd_parser import CENESDPalmSensParser

        return CENESDPalmSensParser(**self.dict())


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


class CENOMEKMC2XASParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import XASParser

        return XASParser(**self.dict())


class CENOMEKMC3XASParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import KMC3XASParser

        return KMC3XASParser(**self.dict())


class CENOMEKMC3BioLogicParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import (
            CENOMEKMC3BioLogicParser,
        )

        return CENOMEKMC3BioLogicParser(**self.dict())


class CENOMETIFParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import CENOMETIFParser

        return CENOMETIFParser(**self.dict())


class CENOMEMassspectrometryParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import MassspectrometryParser

        return MassspectrometryParser(**self.dict())


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
        from nomad_chemical_energy.parsers.dlr_electro_chemistry_parser import (
            DLRECCPParser,
        )

        return DLRECCPParser(**self.dict())


class DLRECCVParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.dlr_electro_chemistry_parser import (
            DLRECCVParser,
        )

        return DLRECCVParser(**self.dict())


class DLRECEISParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.dlr_electro_chemistry_parser import (
            DLRECEISParser,
        )

        return DLRECEISParser(**self.dict())


class CatlabParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.hzb_catlab_parser import CatlabParser

        return CatlabParser(**self.dict())


class GeneralProcessParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.hzb_general_parser import (
            GeneralProcessParser,
        )

        return GeneralProcessParser(**self.dict())


class GeneralNomeParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import GeneralNomeParser

        return GeneralNomeParser(**self.dict())


class TFCSputteringParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.tfc_parser import TFCSputteringParser

        return TFCSputteringParser(**self.dict())


class TFCXRFLibraryParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.tfc_parser import TFCXRFParser

        return TFCXRFParser(**self.dict())


class TFCXRDLibraryParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.tfc_parser import TFCXRDParser

        return TFCXRDParser(**self.dict())


ce_amcc_biologic_parser = CEAMCCBioLogicParserEntryPoint(
    name='CEAMCCBioLogicParser',
    description='Parser for CEAMCC mpr files of BioLogic/EC-Lab potentiostats',
    mainfile_name_re=r'^.*\.mpr',
)

ce_necc_xlsx_parser = CENECCxlsxParserEntryPoint(
    name='CENECCxlsxParser',
    description='Parser for CENECC xls files',
    mainfile_name_re=r'^.*\.xlsx$',
    mainfile_mime_re='(application|text)/.*',
)

ce_necc_biologic_parser = CENECCBioLogicParserEntryPoint(
    name='CENECCBioLogicParser',
    description='Parser for CENECC mpr files of BioLogic/EC-Lab potentiostats',
    mainfile_name_re=r'^.*\.mpr',
)

ce_nesd_biologic_parser = CENESDBioLogicParserEntryPoint(
    name='CENESDBioLogicParser',
    description='Parser for CENESD mpr files of BioLogic/EC-Lab potentiostats',
    mainfile_name_re=r'^.*\.mpr',
)

ce_nesd_zahner_parser = CENESDZahnerParserEntryPoint(
    name='CENESDZahnerParser',
    description='Parser for CENESD isw,ism files of Zahner potentiostats',
    mainfile_name_re=r'^.*\.(isw|ism|isc)',
)

ce_nesd_labview_parser = CENESDLabviewParserEntryPoint(
    name='CENESDLabviewParser',
    description='Parser for CENESD LabVIEW Electrolyser files',
    mainfile_name_re=r'^.*\.tdms',
    mainfile_binary_header_re=r"[\s\S]*TDSm[\s\S]*'Measurements'[\s\S]*'Informations'[\s\S]*",
)

ce_nesd_palmsens_parser = CENESDPalmSensParserEntryPoint(
    name='CENESDPalmSensParser',
    description='Parser for CENESD csv files of PalmSens potentiostats',
    # mainfile_name_re=r'^.*\.csv',
    mainfile_name_re=r'somefilename.csv',
)

ce_nome_gamry_parser = CENOMEGamryParserEntryPoint(
    name='CENOMEGamryParser',
    description='Parser for CENOME Gamry files',
    mainfile_name_re=r'^(.*\.DTA)$',
)

ce_nome_csv_parser = CENOMEcsvParserEntryPoint(
    name='CENOMEcsvParser',
    description='Parser for CENOME csv files',
    mainfile_name_re=r'^(.+\.(pump|oxy)\.(csv|xlsx))$',
    mainfile_mime_re='(application|text)/.*',
)

ce_nome_uvvis_parser = CENOMEUVvisParserEntryPoint(
    name='CENOMEUVvisParser',
    description='Parser for CENOME uvvis files',
    mainfile_name_re=r'^(.*\.(csv|ABS))$',
    mainfile_contents_re=r'^(.*)(\r\n|\r|\n)((WL\/nm,Abs)|("  ABSOR->  Wave:.*))',
)

kmc2_xas_parser = CENOMEKMC2XASParserEntryPoint(
    name='CENOMEKMC2XASParser',
    description='Parser for CENOME xas kmc2 files',
    mainfile_name_re=r'^(.*(\.dat))',
    mainfile_contents_re='/home/kmc2/data/',
)

kmc3_xas_parser_before2021 = CENOMEKMC3XASParserEntryPoint(
    name='CENOMEKMC3XASParser',
    description='Parser for CENOME xas kmc3 files without header',
    mainfile_name_re=r'^(.*\.\d{3})$',
    mainfile_contents_re=r'[\d\.\-eE\t\n]+',
    mainfile_mime_re=r'(text\/plain).*',
)

kmc3_xas_parser = CENOMEKMC3XASParserEntryPoint(
    name='CENOMEKMC3XASParser',
    description='Parser for CENOME xas kmc3 files',
    mainfile_name_re=r'^(.*\.\d{4})$',
    mainfile_contents_re=r'fluo.*ICR.*OCR.*LT',
    mainfile_mime_re=r'(text\/plain).*',
)

kmc3_biologic_parser = CENOMEKMC3BioLogicParserEntryPoint(
    name='KMC3CENOMEBioLogicParser',
    description='Parser for in situ measurements at the KMC3 beamline. Parser reads mpr files of BioLogic/EC-Lab potentiostat.',
    mainfile_name_re=r'^.*\.mpr',
)

ce_nome_tif_parser = CENOMETIFParserEntryPoint(
    name='CENOMETIFParser',
    description='Parser for CENOME tif files',
    mainfile_name_re=r'^(.*(\.tif|\.tiff))',
    mainfile_mime_re='image/.*',
)

ce_nome_massspectrometry_parser = CENOMEMassspectrometryParserEntryPoint(
    name='MassspectrometryParser',
    description='Parser for CE-NOME Massspectrometry files',
    mainfile_name_re=r'^(.*(\.txt))',
    mainfile_contents_re='^.*Spectra International Data File',
)

ce_wannsee_cor_parser = CEWannseeCORParserEntryPoint(
    name='CEWannseeCORParser',
    description='Parser for Wannsee cor files',
    mainfile_name_re=r'^.*\.cor$',
)

ce_wannsee_xrd_xy_parser = CEWannseeXRDParserEntryPoint(
    name='CEWannseeXRDParser',
    description='Parser for Wannsee xy xrd files',
    mainfile_name_re=r'^(.+\.?.+.xy)$',
)

dlr_ec_cv_parser = DLRECCVParserEntryPoint(
    name='DLRECCVParser',
    description='Parser for DLR CV files',
    mainfile_contents_re=r'^.*\nPotential\sapplied\s\(V\)\tTime\s\(s\)\tWE\(1\).Current\s\(A\)\tScan\tIndex',
)

dlr_ec_cp_parser = DLRECCPParserEntryPoint(
    name='DLRECCPParser',
    description='Parser for DLR CP files',
    mainfile_contents_re=r'^(.*)\nTime\s\(s\)\tWE\(1\).Potential\s\(V\)\tCorrected\stime\s\(s\)\tIndex',
)

dlr_ec_eis_parser = DLRECEISParserEntryPoint(
    name='DLRECEISParser',
    description='Parser for DLR EIS files',
    mainfile_contents_re=r"^.*\nIndex\tFrequency\s\(Hz\)\tZ'\s\(Ω\)\s-Z''\s\(Ω\)\tZ\s\(Ω\)\s-Phase\s\(°\)\tTime\s\(s\)",
)

hzb_catlab_parser = CatlabParserEntryPoint(
    name='CatlabParser',
    description='Parser for Catlab files',
    mainfile_name_re=r'^.*CatID[0-9].*#.*$',
    mainfile_mime_re='.*/.*',
)

hzb_general_process_parser = GeneralProcessParserEntryPoint(
    name='GeneralProcessParser',
    description='Parser for general files starting with a sample id',
    mainfile_name_re=r'^.*[A-Z][a-z][A-Z][a-z]\d{4}(-.*)?\.(?!.*\.*pynb$|.*\.*py$|.*\.*archive\.json$|.*\.*json$)[a-zA-Z0-9.]+$',
)

ce_nome_general_parser = GeneralNomeParserEntryPoint(
    name='GeneralNomeParser',
    description='Parser for general files starting with a NOME sample id',
    mainfile_name_re=r'^.*CE-NOME_[A-Z][a-z][A-Z][a-z](_\d{6})?_\d{4}(?!.*\.json$|.*\.*py$|.*\.*pynb$)[a-zA-Z0-9.]+$',
    level=2,
)

tfc_sputtering_parser = TFCSputteringParserEntryPoint(
    name='TFCSputteringParser',
    description='Parse xlsx files with sputtering information. Files are defined for the Thin Film Catalysis Group.',
    mainfile_name_re=r'.+\.xlsx',
    mainfile_mime_re=r'^(application\/vnd\.(openxmlformats-officedocument\.spreadsheetml\.sheet|oasis\.opendocument\.spreadsheet))$',
    mainfile_contents_dict={
        'Parameters': {'__has_all_keys': ['Process/Steps  (i.e., layer)']},
        'Observables': {'__has_all_keys': ['Sputtering', 'Values']},
        # '__comment_symbol': '#',
    },
)

tfc_xrf_parser = TFCXRFLibraryParserEntryPoint(
    name='TFCXRFParser',
    description='Parse txt files with xrf. Files are defined for the Thin Film Catalysis Group.',
    mainfile_name_re=r'.*(R|r)eport.txt',
    mainfile_contents=r'.*Basis.*Grid_',
)

tfc_xrd_parser = TFCXRDLibraryParserEntryPoint(
    name='TFCXRDParser',
    description='Parse txt files with xrd. Files are defined for the Thin Film Catalysis Group.',
    mainfile_name_re=r'.*log_all.txt',
    mainfile_contents=r'########## start Header ##########.*# xlab 0.6.4 log all file',
)
