from nomad.config.models.plugins import ParserEntryPoint


class CEAMCCBioLogicParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_amcc_parser import CEAMCCBioLogicParser

        return CEAMCCBioLogicParser(**self.model_dump())


class CENECCxlsxParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_necc_parser import NECCXlsxParser

        return NECCXlsxParser(**self.model_dump())


class CENECCBioLogicParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_necc_parser import CENECCBioLogicParser

        return CENECCBioLogicParser(**self.model_dump())


class CEACMDBioLogicParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_acmd_parser import CEACMDBioLogicParser

        return CEACMDBioLogicParser(**self.model_dump())


class CEACMDZahnerParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_acmd_parser import CEACMDZahnerParser

        return CEACMDZahnerParser(**self.model_dump())


class CEACMDCHIBinParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_acmd_parser import CEACMDCHIParser

        return CEACMDCHIParser(**self.model_dump())


class CEACMDCHITxtParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_acmd_parser import CEACMDCHIParser

        return CEACMDCHIParser(**self.model_dump())


class CEACMDLabviewParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_acmd_parser import CEACMDLabviewParser

        return CEACMDLabviewParser(**self.model_dump())


class CEACMDPalmSensParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_acmd_parser import CEACMDPalmSensParser

        return CEACMDPalmSensParser(**self.model_dump())


class CEACMDMetadataExcelParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_acmd_parser import (
            CEACMDMetadataExcelParser,
        )

        return CEACMDMetadataExcelParser(**self.model_dump())


class CENOMEGamryParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import GamryParser

        return GamryParser(**self.model_dump())


class CENOMEcsvParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import CENOMEcsvParser

        return CENOMEcsvParser(**self.model_dump())


class CENOMEUVvisParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import UVvisParser

        return UVvisParser(**self.model_dump())


class CENOMEKMC2XASParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import XASParser

        return XASParser(**self.model_dump())


class CENOMEKMC3XASParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import KMC3XASParser

        return KMC3XASParser(**self.model_dump())


class CENOMEKMC3BioLogicParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import (
            CENOMEKMC3BioLogicParser,
        )

        return CENOMEKMC3BioLogicParser(**self.model_dump())


class CENOMETIFParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import CENOMETIFParser

        return CENOMETIFParser(**self.model_dump())


class CENOMEMassspectrometryParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import MassspectrometryParser

        return MassspectrometryParser(**self.model_dump())


class CEWannseeCORParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_wannsee_parser import CORParser

        return CORParser(**self.model_dump())


class CEWannseeXRDParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_wannsee_parser import XRDParser

        return XRDParser(**self.model_dump())


class DLRECCPParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.dlr_electro_chemistry_parser import (
            DLRECCPParser,
        )

        return DLRECCPParser(**self.model_dump())


class DLRECCVParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.dlr_electro_chemistry_parser import (
            DLRECCVParser,
        )

        return DLRECCVParser(**self.model_dump())


class DLRECEISParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.dlr_electro_chemistry_parser import (
            DLRECEISParser,
        )

        return DLRECEISParser(**self.model_dump())


class CatlabParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.hzb_catlab_parser import CatlabParser

        return CatlabParser(**self.model_dump())


class GeneralProcessParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.hzb_general_parser import (
            GeneralProcessParser,
        )

        return GeneralProcessParser(**self.model_dump())


class GeneralNomeParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.ce_nome_parser import GeneralNomeParser

        return GeneralNomeParser(**self.model_dump())


class TFCSputteringParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.tfc_parser import TFCSputteringParser

        return TFCSputteringParser(**self.model_dump())


class TFCXRFLibraryParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.tfc_parser import TFCXRFParser

        return TFCXRFParser(**self.model_dump())


class TFCXRDLibraryParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.tfc_parser import TFCXRDParser

        return TFCXRDParser(**self.model_dump())


class PublicShowcaseParserEntryPoint(ParserEntryPoint):
    def load(self):
        from nomad_chemical_energy.parsers.public_showcase_parser import (
            PublicShowcaseParser,
        )

        return PublicShowcaseParser(**self.model_dump())


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

ce_nesd_biologic_parser = CEACMDBioLogicParserEntryPoint(
    name='CEACMDBioLogicParser',
    description='Parser for CEACMD mpr files of BioLogic/EC-Lab potentiostats',
    mainfile_name_re=r'^.*\.mpr',
)

ce_nesd_zahner_parser = CEACMDZahnerParserEntryPoint(
    name='CEACMDZahnerParser',
    description='Parser for CEACMD isw,ism files of Zahner potentiostats',
    mainfile_name_re=r'^.*\.(isw|ism|isc)',
)

ce_nesd_chi_bin_parser = CEACMDCHIBinParserEntryPoint(
    name='CEACMDCHIBinParser',
    description='Parser for CEACMD bin files of CHI potentiostats',
    mainfile_name_re=r'^.*\.(bin)',
    mainfile_binary_header=b'\x80\xf2\x1d\x00',
)

ce_nesd_chi_txt_parser = CEACMDCHITxtParserEntryPoint(
    name='CEACMDCHITxtParser',
    description='Parser for CEACMD txt files of CHI potentiostats',
    mainfile_name_re=r'^.*\.(txt)',
    mainfile_contents_re=r'Instrument Model:  CHI760E',
)

ce_nesd_labview_parser = CEACMDLabviewParserEntryPoint(
    name='CEACMDLabviewParser',
    description='Parser for CEACMD LabVIEW Electrolyser files',
    mainfile_name_re=r'^.*\.tdms',
    mainfile_binary_header_re=r"[\s\S]*TDSm[\s\S]*'Measurements'[\s\S]*'Informations'[\s\S]*",
)

ce_nesd_palmsens_parser = CEACMDPalmSensParserEntryPoint(
    name='CEACMDPalmSensParser',
    description='Parser for CEACMD csv files of PalmSens potentiostats',
    # mainfile_name_re=r'^.*\.csv',
    mainfile_name_re=r'^.*\.pssession',
)

ce_nesd_metadata_parser = CEACMDMetadataExcelParserEntryPoint(
    name='CEACMDMetadataExcelParser',
    description='Parser for CEACMD xlsx files containing metadata about electrodes, electrolytes, sample information',
    mainfile_name_re=r'.+\.xlsx',
    mainfile_mime_re=r'^(application\/vnd\.(openxmlformats-officedocument\.spreadsheetml\.sheet|oasis\.opendocument\.spreadsheet))$',
    mainfile_contents_dict={
        'ACMD Metadata': {'__has_all_keys': ['Field', 'Value', 'Unit']},
    },
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
    mainfile_contents_re=r'.*Basis.*Grid_',
)

tfc_xrd_parser = TFCXRDLibraryParserEntryPoint(
    name='TFCXRDParser',
    description='Parse txt files with xrd. Files are defined for the Thin Film Catalysis Group.',
    mainfile_name_re=r'.*log_all.txt',
    mainfile_contents_re=r'########## start Header ##########.*# xlab 0.6.4 log all file',
)

public_showcase_parser = PublicShowcaseParserEntryPoint(
    name='EMARShowcaseParser',
    description='Parse txt files with time and pH data. '
    'Files are defined for simplified science communication experiments '
    'regarding the EMAR (Electrochemically-Mediated Amine Regeneration) setup.',
    mainfile_name_re=r'.*\.txt',
    mainfile_contents_re=r'Time pH.*\nRun 1, started.*\nhh:mm:ss pH',
)
