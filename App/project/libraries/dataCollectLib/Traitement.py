from Traitement_Fonctions import *


# ---------- Definition des fonctions de traitements ---------- #



to_num = lambda d, col: pd.to_numeric(d[col], errors='raise')
to_date = lambda d, col: pd.to_datetime(d[col])
to_pos_col = lambda d, col: d[col].map(to_pos)
to_pos_list_col = lambda d, col: d[col].map(to_pos_list)



# -------- Definition des dictionnaires de traitements -------- #


# TB_ARRET_P :: WFS

dict_TB_ARRET_P = {'CAMPGPS':     to_date,
                   'CDATE':       to_date,
                   'DATECREA':    to_date,
                   'DATEDEPL':    to_date,
                   'DATEGEAR':    to_date,
                   'DATEGEMO':    to_date,
                   'DATEGEVO':    to_date,
                   'MDATE':       to_date,
                   'CODEPOST':    to_num, 
                   'GEOM_O':      to_num, 
                   'GID':         to_num, 
                   'IDENT':       to_num, 
                   'IDMOUVT':     to_num, 
                   'LONGARR':     to_num,
                   'REFMOB3':     to_num,  #float
                   'lowerCorner': to_pos_col, 
                   'pos':         to_pos_col, 
                   'upperCorner': to_pos_col }

# SV_ARRET_P :: WFS

dict_SV_ARRET_P = {'CDATE':       to_date, 
                   'MDATE':       to_date, 
                   'GEOM_O':      to_num, 
                   'GID':         to_num, 
                   'lowerCorner': to_pos_col, 
                   'pos':         to_pos_col, 
                   'upperCorner': to_pos_col}

# TB_CHEMIN_L :: WFS

dict_TB_CHEMIN_L = {'CDATE':       to_date, 
                    'DATECHEM':    to_date, 
                    'MDATE':       to_date,
                    'GID':         to_num,
                    'IDARDEB':     to_num,
                    'IDARFIN':     to_num,
                    'IDENT':       to_num,
                    'NBPARJOE':    to_num,
                    'NBPARJOH':    to_num,
                    'NOMCOMLI':    to_num,
                    'NUMEXPLO':    to_num,
                    'RH_TB_LIGNE': to_num, 
                    'LONGCHEM':    to_num ,  #float
                    'lowerCorner': to_pos_col, 
                    'upperCorner': to_pos_col,
                    'posList':     to_pos_list_col}

# SV_CHEM_A :: 

# SV_COURS_A ::

# SV_DEVIA_A ::

# SV_HORAI_A ::

# TB_LIGNE_A ::

# SV_LIGNE_A ::

# SV_MESSA_A ::

# CI_PASSA_P :: WFS

dict_CI_PASSA_P = {'HEURE':       to_date,
                   'GID':         to_num,
                   'IDENT':       to_num,
                   'lowerCorner': to_pos_col,
                   'pos' :        to_pos_col, 
                   'upperCorner': to_pos_col }

# TB_STVEL_P :: WFS
# TODO : TERMBANC (OUI/NON) 
dict_TB_STVEL_P = {'CDATE':       to_date, 
                   'MDATE':       to_date,
                   'GEOM_O':      to_num, 
                   'GID':         to_num, 
                   'IDENT':       to_num, 
                   'NBSUPPOR':    to_num, 
                   'NUMSTAT':     to_num, 
                   'lowerCorner': to_pos_col, 
                   'pos':         to_pos_col, 
                   'upperCorner': to_pos_col }

# CI_VCUB_P :: WFS

dict_CI_VCUB_P = {'HEURE':       to_date, 
                  'GID':         to_num, 
                  'IDENT':       to_num, 
                  'NBPLACES':    to_num, 
                  'NBVELOS':     to_num,
                  'lowerCorner': to_pos_col,
                  'pos' :        to_pos_col, 
                  'upperCorner': to_pos_col }

# SV_TRONC_L :: WFS 

dict_SV_TRONC_L = {'CDATE':            to_date, 
                   'MDATE':            to_date,
                   'DEVIE':            to_num,
                   'GID':              to_num,
                   'ORDRE':            to_num,
                   'RG_SV_ARRET_P_NA': to_num,
                   'RG_SV_ARRET_P_ND': to_num,
                   'RS_SV_CHEM_A':     to_num,
                   'RS_SV_DEVIA_A':    to_num,
                   'lowerCorner':      to_pos_col, 
                   'upperCorner':      to_pos_col,
                   'posList':          to_pos_list_col}

# SV_VEHIC_P :: WFS
#TODO : colonne ARRET (0/1)
dict_SV_VEHIC_P = {'MDATE':             to_date,
                   'BLOQUE':             to_num,
                   'GEOM_O':             to_num,
                   'GID':                to_num,
                   'LOCALISATION':       to_num,
                   'NEUTRALISE':         to_num,
                   'PMR':                to_num,
                   'RETARD':             to_num,
                   'RS_SV_ARRET_P_ACTU': to_num,
                   'RS_SV_ARRET_P_SUIV': to_num,
                   'RS_SV_CHEM_A':       to_num,
                   'RS_SV_COURS_A':      to_num,
                   'RS_SV_LIGNE_A':      to_num,
                   'SAE':                to_num,
                   'VITESSE':            to_num,
                   'lowerCorner':        to_pos_col,
                   'pos' :               to_pos_col, 
                   'upperCorner':        to_pos_col }


# ---------- Fonctions d'appication des traitements ----------- #


def treatment(df, ops):
    for col, op in ops.items() :
        df[col] = op(df, col)
    return df


# ------------------------ Traitements ------------------------ #


