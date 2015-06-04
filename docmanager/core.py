#
# Copyright (c) 2014-2015 SUSE Linux GmbH
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of version 3 of the GNU General Public License as
# published by the Free Software Foundation.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, contact SUSE LLC.
#
# To contact SUSE about this file by physical or electronic mail,
# you may find current contact information at www.suse.com

NS = {
        "d":"http://docbook.org/ns/docbook",
        "dm":"urn:x-suse:ns:docmanager"
}

DefaultDocManagerProperties = [
        "maintainer",
        "status",
        "deadline",
        "priority",
        "translation",
        "languages"
]

class ReturnCodes():
    E_OK = 0
    E_FILE_NOT_FOUND = 1
    E_COULD_NOT_SET_VALUE = 2
    E_XML_PARSE_ERROR = 3
    E_DAPS_ERROR = 4
    E_INVALID_USAGE_KEYVAL = 5
    E_METHOD_NOT_IMPLEMENTED = 6
    E_INFO_ELEMENT_MISSING = 7
    E_CALL_WITHOUT_PARAMS = 8
    E_INVALID_XML_DOCUMENT = 9
    E_WRONG_INPUT_FORMAT = 10

VALIDROOTS = ('abstract', 'address', 'annotation', 'audiodata',
              'audioobject', 'bibliodiv', 'bibliography', 'bibliolist',
              'bibliolist', 'blockquote', 'book', 'calloutlist',
              'calloutlist', 'caption', 'caution', 'classsynopsis',
              'classsynopsisinfo', 'cmdsynopsis', 'cmdsynopsis', 'components',
              'constraintdef', 'constructorsynopsis', 'destructorsynopsis',
              'epigraph', 'equation', 'equation', 'example', 'fieldsynopsis',
              'figure', 'formalpara', 'funcsynopsis', 'funcsynopsisinfo',
              'glossary', 'glossary', 'glossdiv', 'glosslist', 'glosslist',
              'imagedata', 'imageobject', 'imageobjectco', 'imageobjectco',
              'important', 'index', 'indexdiv', 'informalequation',
              'informalequation', 'informalexample', 'informalfigure',
              'informaltable', 'inlinemediaobject', 'itemizedlist', 'legalnotice',
              'literallayout', 'mediaobject', 'methodsynopsis', 'msg', 'msgexplan',
              'msgmain', 'msgrel', 'msgset', 'msgsub', 'note', 'orderedlist',
              'para', 'part', 'partintro', 'personblurb', 'procedure',
              'productionset', 'programlisting', 'programlistingco',
              'programlistingco', 'qandadiv', 'qandaentry', 'qandaset',
              'qandaset', 'refentry', 'refsect1', 'refsect2', 'refsect3',
              'refsection', 'refsynopsisdiv', 'revhistory', 'screen', 'screenco',
              'screenco', 'screenshot', 'sect1', 'sect2', 'sect3', 'sect4', 'sect5',
              'section', 'segmentedlist', 'set', 'set', 'setindex', 'sidebar',
              'simpara', 'simplelist', 'simplesect', 'step', 'stepalternatives',
              'synopsis', 'table', 'task', 'taskprerequisites', 'taskrelated',
              'tasksummary', 'textdata', 'textobject', 'tip', 'toc', 'tocdiv',
              'topic', 'variablelist', 'videodata', 'videoobject', 'warning')

LANGUAGES = (
    # A
    'aa_DJ', 'aa', 'aa_ER', 'aa_ET', 'af_ZA', 'af', 'ak_GH', 'ak', 'am_ET',
    'am', 'an_ES', 'an', 'anp_IN', 'anp', 'ar_AE', 'ar', 'ar_BH', 'ar_DZ',
    'ar_EG', 'ar_IN', 'ar_IQ', 'ar_JO', 'ar_KW', 'ar_LB', 'ar_LY', 'ar_MA',
    'ar_OM', 'ar_QA', 'ar_SA', 'ar_SD', 'ar_SS', 'ar_SY', 'ar_TN', 'ar_YE',
    'as_IN', 'as', 'ast_ES', 'ast', 'ayc_PE', 'ayc', 'az_AZ', 'az',
    # B
    'be_BY', 'be', 'bem_ZM', 'bem', 'ber_DZ', 'ber', 'ber_MA', 'bg_BG', 'bg',
    'bho_IN', 'bho', 'bn_BD', 'bn', 'bn_IN', 'bo_CN', 'bo', 'bo_IN', 'br_FR',
    'br', 'brx_IN', 'brx', 'bs_BA', 'bs', 'byn_ER', 'byn',
    # C
    'ca_AD', 'ca', 'ca_ES', 'ca_FR', 'ca_IT', 'cmn_TW', 'cmn', 'crh_UA',
    'crh', 'csb_PL', 'csb', 'cs_CZ', 'cs', 'cv_RU', 'cv', 'cy_GB', 'cy',
    # D
    'da_DK', 'da', 'de_AT', 'de', 'de_BE', 'de_CH', 'de_DE', 'de_LU',
    'doi_IN', 'doi', 'dv_MV', 'dv', 'dz_BT', 'dz',
    # E
    'el_CY', 'el',
    'el_GR', 'en_AG', 'en', 'en_AU', 'en_BE', 'en_BW', 'en_CA', 'en_DK',
    'en_GB', 'en_HK', 'en_IE', 'en_IN', 'en_NG', 'en_NZ', 'en_PH', 'en_SG',
    'en_US', 'en_ZA', 'en_ZM', 'en_ZW', 'es_AR', 'es', 'es_BO', 'es_CL',
    'es_CO', 'es_CR', 'es_CU', 'es_DO', 'es_EC', 'es_ES', 'es_GT', 'es_HN',
    'es_MX', 'es_NI', 'es_PA', 'es_PE', 'es_PR', 'es_PY', 'es_SV', 'es_US',
    'es_UY', 'es_VE', 'et_EE', 'et', 'eu_ES', 'eu',
    # F
    'fa_IR', 'fa', 'ff_SN', 'ff', 'fi_FI', 'fi', 'fil_PH', 'fil',
    'fo_FO', 'fo', 'fr_BE', 'fr', 'fr_CA', 'fr_CH', 'fr_FR', 'fr_LU',
    'fur_IT', 'fur', 'fy_DE', 'fy', 'fy_NL',
    # G
    'ga_IE', 'ga', 'gd_GB', 'gd', 'gez_ER', 'gez', 'gez_ET', 'gl_ES', 'gl',
    'gu_IN', 'gu', 'gv_GB', 'gv',
    # H
    'hak_TW',
    'hak', 'ha_NG', 'ha', 'he_IL', 'he', 'hi_IN', 'hi', 'hne_IN', 'hne',
    'hr_HR', 'hr', 'hsb_DE', 'hsb', 'ht_HT', 'ht', 'hu_HU', 'hu', 'hy_AM',
    'hy',
    # I
    'ia_FR', 'ia', 'id_ID', 'id', 'ig_NG', 'ig', 'ik_CA', 'ik',
    'is_IS', 'is', 'it_CH', 'it', 'it_IT', 'iu_CA', 'iu', 'iw_IL', 'iw',
    # K
    'ka_GE', 'ka', 'kk_KZ', 'kk', 'kl_GL', 'kl', 'km_KH', 'km', 'kn_IN',
    'kn', 'kok_IN', 'kok', 'ks_IN', 'ks', 'ku_TR', 'ku', 'kw_GB', 'kw',
    'ky_KG', 'ky',
    # L
    'lb_LU', 'lb', 'lg_UG', 'lg', 'li_BE', 'li', 'lij_IT', 'lij', 'li_NL',
    'lo_LA', 'lo', 'lt_LT', 'lt', 'lv_LV', 'lv', 'lzh_TW', 'lzh',
    # M
    'mag_IN', 'mag', 'mai_IN', 'mai', 'mg_MG', 'mg', 'mhr_RU', 'mhr',
    'mi_NZ', 'mi', 'mk_MK', 'mk', 'ml_IN', 'ml', 'mni_IN', 'mni', 'mn_MN',
    'mn', 'mr_IN', 'mr', 'ms_MY', 'ms', 'mt_MT', 'mt', 'my_MM', 'my',
    # N
    'nan_TW', 'nan', 'nb_NO', 'nb', 'nds_DE', 'nds', 'nds_NL', 'ne_NP', 'ne',
    'nhn_MX', 'nhn', 'niu_NU', 'niu', 'niu_NZ', 'nl_AW', 'nl', 'nl_BE',
    'nl_NL', 'nn_NO', 'nn', 'no_NO', 'no', 'nr_ZA', 'nr', 'nso_ZA', 'nso',
    # O
    'oc_FR', 'oc', 'om_ET', 'om', 'om_KE', 'or_IN', 'or', 'os_RU', 'os',
    # P
    'pa_IN', 'pa', 'pap_AN', 'pap', 'pap_AW', 'pap_CW', 'pa_PK', 'pl_PL',
    'pl', 'POSIX', 'ps_AF', 'ps', 'pt_BR', 'pt', 'pt_PT',
    # Q
    'quz_PE', 'quz',
    # R
    'ro_RO', 'ro', 'ru_RU', 'ru', 'ru_UA', 'rw_RW', 'rw',
    # S
    'sa_IN', 'sa', 'sat_IN', 'sat', 'sc_IT', 'sc', 'sd_IN', 'sd', 'se_NO',
    'se', 'shs_CA', 'shs', 'sh_YU', 'sh', 'sid_ET', 'sid', 'si_LK', 'si',
    'sk_SK', 'sk', 'sl_SI', 'sl', 'so_DJ', 'so', 'so_ET', 'so_KE', 'so_SO',
    'sq_AL', 'sq', 'sq_MK', 'sr_ME', 'sr', 'sr_RS', 'ss_ZA', 'ss', 'st_ZA',
    'st', 'sv_FI', 'sv', 'sv_SE', 'sw_KE', 'sw', 'sw_TZ', 'szl_PL', 'szl',
    # T
    'ta_IN', 'ta', 'ta_LK', 'te_IN', 'te', 'tg_TJ', 'tg', 'the_NP', 'the',
    'th_TH', 'th', 'ti_ER', 'ti', 'ti_ET', 'tig_ER', 'tig', 'tk_TM', 'tk',
    'tl_PH', 'tl', 'tn_ZA', 'tn', 'tr_CY', 'tr', 'tr_TR', 'ts_ZA', 'ts',
    'tt_RU', 'tt',
    # U
    'ug_CN', 'ug', 'uk_UA', 'uk', 'unm_US', 'unm', 'ur_IN', 'ur', 'ur_PK',
    'uz_UZ', 'uz',
    # V
    've_ZA', 've', 'vi_VN', 'vi',
    # W
    'wa_BE', 'wa', 'wae_CH', 'wae', 'wal_ET', 'wal', 'wo_SN', 'wo',
    # X
    'xh_ZA', 'xh',
    # Y
    'yi_US', 'yi', 'yo_NG', 'yo', 'yue_HK', 'yue',
    # Z
    'zh_CN', 'zh', 'zh_HK', 'zh_SG', 'zh_TW', 'zu_ZA', 'zu'
    )