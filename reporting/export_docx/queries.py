class Query:

    @staticmethod
    def orcl_npls():
        return '''
            SELECT 
                ROW_NUMBER() Over (Order By NVL(SUM(C.VSEGO_ZADOLJENNOST), 0) DESC) Numeral,
                UNIQUE_CODE as id,
                MAX(NAME_CLIENT) as Name, 
                MAX(B.NAME) as Branch,
                NVL(SUM(VSEGO_ZADOLJENNOST)/1000000,0) as Balans
            FROM CREDITS C
            LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = C.REPORT_ID
            LEFT JOIN CREDITS_BRANCH B ON B.CODE = C.MFO
            LEFT JOIN VIEW_OVERDUE_GROUPS O ON O.LOANID = C.CODE_CONTRACT AND O.REPORT_ID = C.REPORT_ID
            WHERE C.REPORT_ID = %s
            GROUP BY UNIQUE_CODE
            HAVING 
                MAX(C.DAYS) > 90 
                OR MAX(C.ARREAR_DAYS) > 90
                OR SUM(C.OSTATOK_SUDEB) IS NOT NULL
                OR SUM(C.OSTATOK_VNEB_PROSR) IS NOT NULL
            ORDER BY BALANS DESC
        '''

    @staticmethod
    def orcl_toxics():
        return '''
            SELECT 
                ROW_NUMBER() Over (Order By NVL(SUM(C.VSEGO_ZADOLJENNOST), 0) DESC) Numeral,
                UNIQUE_CODE as id,
                MAX(NAME_CLIENT) as Name, 
                MAX(B.NAME) as Branch,
                NVL(SUM(VSEGO_ZADOLJENNOST)/1000000,0) as Balans
            FROM CREDITS C
            LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = C.REPORT_ID
            LEFT JOIN CREDITS_BRANCH B ON B.CODE = C.MFO
            WHERE REPORT_ID = %s
            GROUP BY UNIQUE_CODE
            HAVING 
                NVL(MAX(C.DAYS),0) <= 90 
                AND NVL(MAX(C.ARREAR_DAYS),0) <= 90
                AND SUM(OSTATOK_SUDEB) IS NULL
                AND SUM(OSTATOK_VNEB_PROSR) IS NULL
                AND SUM(OSTATOK_PERESM) IS NOT NULL
            ORDER BY BALANS DESC
        '''

    @staticmethod
    def orcl_overdues():
        return '''
            SELECT 
                ROW_NUMBER() Over (Order By NVL(SUM(C.OSTATOK_PROSR), 0) DESC) Numeral,
                UNIQUE_CODE as id,
                MAX(NAME_CLIENT) as Name, 
                MAX(B.NAME) as Branch,
                NVL(SUM(OSTATOK_PROSR)/1000000,0) as Balans
            FROM CREDITS C
            LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = C.REPORT_ID
            LEFT JOIN CREDITS_BRANCH B ON B.CODE = C.MFO
            WHERE REPORT_ID = %s
            GROUP BY UNIQUE_CODE
            HAVING SUM(OSTATOK_PROSR) <> 0
            ORDER BY BALANS DESC
            --FETCH FIRST 200 ROWS ONLY    
                '''

    @staticmethod
    def orcl_byterms():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, DAYS, ARREAR_DAYS, OSTATOK_SUDEB, 
                OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS 
                (
                    SELECT
                        CASE WHEN TERM > 10 THEN 1
                            WHEN TERM > 7 AND TERM <= 10 THEN 2
                            WHEN TERM > 5 AND TERM <= 7 THEN 3
                            WHEN TERM > 2 AND TERM <= 5 THEN 4
                            ELSE 5 END AS GROUPS, 
                        CREDITS.UNIQUE_CODE,
                        DAYS,
                        ARREAR_DAYS,
                        OSTATOK_SUDEB, 
                        OSTATOK_VNEB_PROSR,
                        OSTATOK_PERESM,
                        OSTATOK_REZERV,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS
                    WHERE REPORT_ID = %s
                ),

                PORTFOLIO_TABLE (GROUPS, BALANS, RESERVE) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST), SUM(OSTATOK_REZERV)
                    FROM REPORT_DATA_TABLE
                    GROUP BY GROUPS
                ),

                NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    WHERE NVL(DAYS,0) > 90 
                        OR NVL(ARREAR_DAYS,0) > 90 
                        OR OSTATOK_SUDEB IS NOT NULL 
                        OR OSTATOK_VNEB_PROSR IS NOT NULL
                    GROUP BY UNIQUE_CODE
                ),

                NPL_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM NPL_UNIQUE_TABLE N
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = N.UNIQUE_CODE
                    GROUP BY GROUPS
                ),

                TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    GROUP BY UNIQUE_CODE
                    HAVING SUM(OSTATOK_PERESM) IS NOT NULL 
                        AND NVL(MAX(DAYS),0) <= 90 
                        AND NVL(MAX(ARREAR_DAYS),0) <= 90 
                        AND SUM(OSTATOK_SUDEB) IS NULL 
                        AND SUM(OSTATOK_VNEB_PROSR) IS NULL
                ),

                TOX_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM TOX_UNIQUE_TABLE T
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = T.UNIQUE_CODE
                    GROUP BY GROUPS
                )
                SELECT 
                    P.GROUPS as id, 
                    G.TITLE as Title, 
                    P.BALANS/1000000 as PorBalans,
                    P.BALANS/X.TOTALS as PorPercent,
                    NVL(N.BALANS,0)/1000000 as NplBalans,
                    NVL(T.BALANS,0)/1000000 as ToxBalans,
                    (NVL(N.BALANS,0)+NVL(T.BALANS,0))/1000000 as AmountNTK,
                    (NVL(N.BALANS,0)+NVL(T.BALANS,0))/P.BALANS as WeightNTK,
                    NVL(P.RESERVE,0)/1000000 as ResBalans,
                    NVL(P.RESERVE,0)/(NVL(N.BALANS,0)+NVL(T.BALANS,0)) as ResCovers                    
                FROM PORTFOLIO_TABLE P
                LEFT JOIN NPL_TABLE N  ON N.GROUPS = P.GROUPS
                LEFT JOIN TOX_TABLE T  ON T.GROUPS = P.GROUPS
                LEFT JOIN VIEW_TERM_NAMES G ON G.GROUPS = P.GROUPS,
                (SELECT SUM(BALANS) as Totals FROM PORTFOLIO_TABLE) X
        '''

    @staticmethod
    def orcl_bysubjects():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, DAYS, ARREAR_DAYS, OSTATOK_SUDEB, 
                OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS 
                (
                    SELECT
                        CASE SUBJECT 
                        WHEN TRANSLATE('ЮЛ' USING nchar_cs) THEN 1 
                        WHEN TRANSLATE('ИП' USING nchar_cs) THEN 2 
                        ELSE 3 END AS GROUPS, 
                        CREDITS.UNIQUE_CODE,
                        DAYS,
                        ARREAR_DAYS,
                        OSTATOK_SUDEB, 
                        OSTATOK_VNEB_PROSR,
                        OSTATOK_PERESM,
                        OSTATOK_REZERV,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS
                    WHERE REPORT_ID = %s
                ),

                PORTFOLIO_TABLE (GROUPS, BALANS, RESERVE) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST), SUM(OSTATOK_REZERV)
                    FROM REPORT_DATA_TABLE
                    GROUP BY GROUPS
                ),

                NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    WHERE NVL(DAYS,0) > 90 
                        OR NVL(ARREAR_DAYS,0) > 90 
                        OR OSTATOK_SUDEB IS NOT NULL 
                        OR OSTATOK_VNEB_PROSR IS NOT NULL
                    GROUP BY UNIQUE_CODE
                ),

                NPL_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM NPL_UNIQUE_TABLE N
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = N.UNIQUE_CODE
                    GROUP BY GROUPS
                ),

                TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    GROUP BY UNIQUE_CODE
                    HAVING SUM(OSTATOK_PERESM) IS NOT NULL 
                        AND NVL(MAX(DAYS),0) <= 90 
                        AND NVL(MAX(ARREAR_DAYS),0) <= 90 
                        AND SUM(OSTATOK_SUDEB) IS NULL 
                        AND SUM(OSTATOK_VNEB_PROSR) IS NULL
                ),

                TOX_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM TOX_UNIQUE_TABLE T
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = T.UNIQUE_CODE
                    GROUP BY GROUPS
                )

            SELECT 
                P.GROUPS as id, 
                G.TITLE as Title, 
                P.BALANS/1000000 as PorBalans,
                P.BALANS/X.TOTALS as PorPercent,
                NVL(N.BALANS,0)/1000000 as NplBalans,
                NVL(T.BALANS,0)/1000000 as ToxBalans,
                (NVL(N.BALANS,0)+NVL(T.BALANS,0))/1000000 as AmountNTK,
                (NVL(N.BALANS,0)+NVL(T.BALANS,0))/P.BALANS as WeightNTK,
                NVL(P.RESERVE,0)/1000000 as ResBalans,
                NVL(P.RESERVE,0)/(NVL(N.BALANS,0)+NVL(T.BALANS,0)) as ResCovers
            FROM PORTFOLIO_TABLE P
            LEFT JOIN NPL_TABLE N  ON N.GROUPS = P.GROUPS
            LEFT JOIN TOX_TABLE T  ON T.GROUPS = P.GROUPS
            LEFT JOIN VIEW_SUBJECT_NAMES G ON G.GROUPS = P.GROUPS,
            (SELECT SUM(BALANS) as Totals FROM PORTFOLIO_TABLE) X
        '''

    @staticmethod
    def orcl_bysegments():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, DAYS, ARREAR_DAYS, OSTATOK_SUDEB, 
                OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS 
                (
                    SELECT
                        SEGMENT AS GROUPS, 
                        CREDITS.UNIQUE_CODE,
                        DAYS,
                        ARREAR_DAYS,
                        OSTATOK_SUDEB, 
                        OSTATOK_VNEB_PROSR,
                        OSTATOK_PERESM,
                        OSTATOK_REZERV,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS
                    WHERE REPORT_ID = %s
                ),

                PORTFOLIO_TABLE (GROUPS, BALANS, RESERVE) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST), SUM(OSTATOK_REZERV)
                    FROM REPORT_DATA_TABLE
                    GROUP BY GROUPS
                ),

                NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    WHERE NVL(DAYS,0) > 90 
                        OR NVL(ARREAR_DAYS,0) > 90 
                        OR OSTATOK_SUDEB IS NOT NULL 
                        OR OSTATOK_VNEB_PROSR IS NOT NULL
                    GROUP BY UNIQUE_CODE
                ),

                NPL_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM NPL_UNIQUE_TABLE N
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = N.UNIQUE_CODE
                    GROUP BY GROUPS
                ),

                TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    GROUP BY UNIQUE_CODE
                    HAVING SUM(OSTATOK_PERESM) IS NOT NULL 
                        AND NVL(MAX(DAYS),0) <= 90 
                        AND NVL(MAX(ARREAR_DAYS),0) <= 90 
                        AND SUM(OSTATOK_SUDEB) IS NULL 
                        AND SUM(OSTATOK_VNEB_PROSR) IS NULL
                ),

                TOX_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM TOX_UNIQUE_TABLE T
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = T.UNIQUE_CODE
                    GROUP BY GROUPS
                )

                SELECT 
                    P.GROUPS as id, 
                    G.TITLE as Title, 
                    P.BALANS/1000000 as PorBalans,
                    P.BALANS/X.TOTALS as PorPercent,
                    NVL(N.BALANS,0)/1000000 as NplBalans,
                    NVL(T.BALANS,0)/1000000 as ToxBalans,
                    (NVL(N.BALANS,0)+NVL(T.BALANS,0))/1000000 as AmountNTK,
                    (NVL(N.BALANS,0)+NVL(T.BALANS,0))/P.BALANS as WeightNTK,
                    NVL(P.RESERVE,0)/1000000 as ResBalans,
                    NVL(P.RESERVE,0)/(NVL(N.BALANS,0)+NVL(T.BALANS,0)) as ResCovers
                FROM PORTFOLIO_TABLE P
                LEFT JOIN NPL_TABLE N  ON N.GROUPS = P.GROUPS
                LEFT JOIN TOX_TABLE T  ON T.GROUPS = P.GROUPS
                LEFT JOIN VIEW_SEGMENT_NAMES G ON G.GROUPS = P.GROUPS,
                (SELECT SUM(BALANS) as Totals FROM PORTFOLIO_TABLE) X
        '''

    @staticmethod
    def orcl_bycurrency():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, DAYS, ARREAR_DAYS, OSTATOK_SUDEB, 
                OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS 
                (
                    SELECT
                        CURRENCY AS GROUPS, 
                        CREDITS.UNIQUE_CODE,
                        DAYS,
                        ARREAR_DAYS,
                        OSTATOK_SUDEB, 
                        OSTATOK_VNEB_PROSR,
                        OSTATOK_PERESM,
                        OSTATOK_REZERV,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS
                    WHERE REPORT_ID = %s
                ),

                PORTFOLIO_TABLE (GROUPS, BALANS, RESERVE) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST), SUM(OSTATOK_REZERV)
                    FROM REPORT_DATA_TABLE
                    GROUP BY GROUPS
                ),

                NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    WHERE NVL(DAYS,0) > 90 
                        OR NVL(ARREAR_DAYS,0) > 90 
                        OR OSTATOK_SUDEB IS NOT NULL 
                        OR OSTATOK_VNEB_PROSR IS NOT NULL
                    GROUP BY UNIQUE_CODE
                ),

                NPL_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM NPL_UNIQUE_TABLE N
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = N.UNIQUE_CODE
                    GROUP BY GROUPS
                ),

                TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    GROUP BY UNIQUE_CODE
                    HAVING SUM(OSTATOK_PERESM) IS NOT NULL 
                        AND NVL(MAX(DAYS),0) <= 90 
                        AND NVL(MAX(ARREAR_DAYS),0) <= 90 
                        AND SUM(OSTATOK_SUDEB) IS NULL 
                        AND SUM(OSTATOK_VNEB_PROSR) IS NULL
                ),

                TOX_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM TOX_UNIQUE_TABLE T
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = T.UNIQUE_CODE
                    GROUP BY GROUPS
                )

            SELECT 
                P.GROUPS as id, 
                G.TITLE as Title, 
                P.BALANS/1000000 as PorBalans,
                P.BALANS/X.TOTALS as PorPercent,
                NVL(N.BALANS,0)/1000000 as NplBalans,
                NVL(T.BALANS,0)/1000000 as ToxBalans,
                (NVL(N.BALANS,0)+NVL(T.BALANS,0))/1000000 as AmountNTK,
                (NVL(N.BALANS,0)+NVL(T.BALANS,0))/P.BALANS as WeightNTK,
                NVL(P.RESERVE,0)/1000000 as ResBalans,
                NVL(P.RESERVE,0)/(NVL(N.BALANS,0)+NVL(T.BALANS,0)) as ResCovers
            FROM PORTFOLIO_TABLE P
            LEFT JOIN NPL_TABLE N  ON N.GROUPS = P.GROUPS
            LEFT JOIN TOX_TABLE T  ON T.GROUPS = P.GROUPS
            LEFT JOIN VIEW_CURRENCY_NAMES G ON G.GROUPS = P.GROUPS,
            (SELECT SUM(BALANS) as Totals FROM PORTFOLIO_TABLE) X
        '''

    @staticmethod
    def orcl_bybranches():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, DAYS, ARREAR_DAYS, OSTATOK_SUDEB, 
                OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS 
                (
                    SELECT
                        BRANCH_SORT AS GROUPS, 
                        CREDITS.UNIQUE_CODE,
                        DAYS,
                        ARREAR_DAYS,
                        OSTATOK_SUDEB, 
                        OSTATOK_VNEB_PROSR,
                        OSTATOK_PERESM,
                        OSTATOK_REZERV,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS
                    WHERE REPORT_ID = %s
                ),

                PORTFOLIO_TABLE (GROUPS, BALANS, RESERVE) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST), SUM(OSTATOK_REZERV)
                    FROM REPORT_DATA_TABLE
                    GROUP BY GROUPS
                ),

                NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    WHERE NVL(DAYS,0) > 90 
                        OR NVL(ARREAR_DAYS,0) > 90 
                        OR OSTATOK_SUDEB IS NOT NULL 
                        OR OSTATOK_VNEB_PROSR IS NOT NULL
                    GROUP BY UNIQUE_CODE
                ),

                NPL_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM NPL_UNIQUE_TABLE N
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = N.UNIQUE_CODE
                    GROUP BY GROUPS
                ),

                TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    GROUP BY UNIQUE_CODE
                    HAVING SUM(OSTATOK_PERESM) IS NOT NULL 
                        AND NVL(MAX(DAYS),0) <= 90 
                        AND NVL(MAX(ARREAR_DAYS),0) <= 90 
                        AND SUM(OSTATOK_SUDEB) IS NULL 
                        AND SUM(OSTATOK_VNEB_PROSR) IS NULL
                ),

                TOX_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM TOX_UNIQUE_TABLE T
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = T.UNIQUE_CODE
                    GROUP BY GROUPS
                )

                SELECT 
                    P.GROUPS as id, 
                    B.NAME as Title, 
                    P.BALANS/1000000 as PorBalans,
                    P.BALANS/X.TOTALS as PorPercent,
                    NVL(N.BALANS,0)/1000000 as NplBalans,
                    NVL(T.BALANS,0)/1000000 as ToxBalans,
                    (NVL(N.BALANS,0)+NVL(T.BALANS,0))/1000000 as AmountNTK,
                    (NVL(N.BALANS,0)+NVL(T.BALANS,0))/P.BALANS as WeightNTK,
                    NVL(P.RESERVE,0)/1000000 as ResBalans,
                    NVL(P.RESERVE,0)/(NVL(N.BALANS,0)+NVL(T.BALANS,0)) as ResCovers
                FROM PORTFOLIO_TABLE P
                LEFT JOIN NPL_TABLE N  ON N.GROUPS = P.GROUPS
                LEFT JOIN TOX_TABLE T  ON T.GROUPS = P.GROUPS
                LEFT JOIN CREDITS_BRANCH B ON B.SORT = P.GROUPS,
                (SELECT SUM(BALANS) as Totals FROM PORTFOLIO_TABLE) X
                ORDER BY P.GROUPS                       
        '''

    @staticmethod
    def orcl_byretailproduct():
        return '''
                WITH 
                    REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, DAYS, ARREAR_DAYS, OSTATOK_SUDEB, OSTATOK_VNEB_PROSR, 
                        OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST, OSTATOK_PROSR, OSTATOK_NACH_PRCNT) AS 
                    (
                        SELECT
                            VID_KREDITOVANIYA, 
                            UNIQUE_CODE,
                            DAYS,
                            ARREAR_DAYS,
                            OSTATOK_SUDEB, 
                            OSTATOK_VNEB_PROSR,
                            OSTATOK_PERESM,
                            OSTATOK_REZERV,
                            VSEGO_ZADOLJENNOST,
                            OSTATOK_PROSR,
                            OSTATOK_NACH_PRCNT
                        FROM CREDITS
                        WHERE REPORT_ID = %s 
                          AND VID_KREDITOVANIYA IN (
                              '30-Потребительский кредит', 
                              '32-Микрозаем', 
                              '34-Автокредит', 
                              '54-Овердрафт по пластиковым карточкам физических лиц', 
                              '59-Образовательный кредит'
                          )
                    ),

                    PORTFOLIO_TABLE (GROUPS, BALANS, PROSR, NACHPRCNT) AS (
                        SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST), SUM(OSTATOK_PROSR), SUM(OSTATOK_NACH_PRCNT)
                        FROM REPORT_DATA_TABLE
                        GROUP BY GROUPS
                    ),

                    NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                        SELECT UNIQUE_CODE
                        FROM REPORT_DATA_TABLE R
                        WHERE NVL(DAYS,0) > 90 
                            OR NVL(ARREAR_DAYS,0) > 90 
                            OR OSTATOK_SUDEB IS NOT NULL 
                            OR OSTATOK_VNEB_PROSR IS NOT NULL
                        GROUP BY UNIQUE_CODE
                    ),

                    NPL_TABLE (GROUPS, BALANS) AS(
                        SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                        FROM NPL_UNIQUE_TABLE N
                        LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = N.UNIQUE_CODE
                        GROUP BY GROUPS
                    )

                SELECT 
                    ROW_NUMBER () OVER (ORDER BY P.GROUPS) AS Numeral,
                    SUBSTR(P.GROUPS,4) as Title, 
                    P.BALANS/1000000 as PorBalans,
                    P.BALANS/X.TOTALS as PorPercent,
                    NVL(P.PROSR,0)/1000000 as PrsBalans,
                    NVL(N.BALANS,0)/1000000 as NplBalans,
                    NVL(N.BALANS,0)/P.BALANS as NplWeight,
                    NVL(P.NACHPRCNT,0)/1000000 as NachBalans
                FROM PORTFOLIO_TABLE P
                LEFT JOIN NPL_TABLE N  ON N.GROUPS = P.GROUPS,
                (SELECT SUM(BALANS) as Totals FROM PORTFOLIO_TABLE) X
                ORDER BY P.GROUPS
            '''

    @staticmethod
    def orcl_bypercentage_national():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, CLIENT_TYPE, PERIOD, VSEGO_ZADOLJENNOST) AS 
                (
                    SELECT
                        CASE WHEN CREDIT_PROCENT > 20 THEN 5
                            WHEN CREDIT_PROCENT > 15 THEN 4 
                            WHEN CREDIT_PROCENT > 10 THEN 3 
                            WHEN CREDIT_PROCENT > 5 THEN 2 
                            ELSE 1 END AS GROUPS, 
                        UNIQUE_CODE,
                        CLIENT_TYPE,
                        SUBSTR(SROK,1,1),
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS
                    WHERE REPORT_ID = %s AND CODE_VAL = '000'
                ),

                UL_LONG_TABLE (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE CLIENT_TYPE LIKE 'J' AND PERIOD = 3
                    GROUP BY GROUPS
                ),

                UL_SHORT_TABLE (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE CLIENT_TYPE LIKE 'J' AND PERIOD = 1
                    GROUP BY GROUPS
                ),

                FL_LONG_TABLE (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE CLIENT_TYPE LIKE 'P' AND PERIOD = 3
                    GROUP BY GROUPS
                ),

                FL_SHORT_TABLE (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE CLIENT_TYPE LIKE 'P' AND PERIOD = 1
                    GROUP BY GROUPS
                )	

            SELECT 
                P.GROUPS AS Numeral,
                P.TITLE as Title, 
                NVL(ULL.BALANS,0)/1000000 AS ULLongTerm,
                NVL(ULS.BALANS,0)/1000000 AS ULShortTerm,
                NVL(FLL.BALANS,0)/1000000 AS FLLongTerm,
                NVL(FLS.BALANS,0)/1000000 AS FLShortTerm,
                NVL(ULL.BALANS,0)/S_ULL.TOTAL AS ULLongPart,
                NVL(ULS.BALANS,0)/S_ULS.TOTAL AS ULShortPart,
                NVL(FLL.BALANS,0)/S_FLL.TOTAL AS FLLongPart,
                NVL(FLS.BALANS,0)/S_FLS.TOTAL AS FLShortPart
            FROM VIEW_PERCENTAGE_NAMES P
            LEFT JOIN UL_LONG_TABLE ULL  ON ULL.GROUPS = P.GROUPS
            LEFT JOIN UL_SHORT_TABLE ULS ON ULS.GROUPS = P.GROUPS
            LEFT JOIN FL_LONG_TABLE FLL  ON FLL.GROUPS = P.GROUPS
            LEFT JOIN FL_SHORT_TABLE FLS ON FLS.GROUPS = P.GROUPS,
            (SELECT SUM(BALANS) AS TOTAL FROM UL_LONG_TABLE) S_ULL,
            (SELECT SUM(BALANS) AS TOTAL FROM UL_SHORT_TABLE) S_ULS,
            (SELECT SUM(BALANS) AS TOTAL FROM FL_LONG_TABLE) S_FLL,
            (SELECT SUM(BALANS) AS TOTAL FROM FL_SHORT_TABLE) S_FLS 
            ORDER BY P.GROUPS
        '''

    @staticmethod
    def orcl_bypercentage_foreign():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, CLIENT_TYPE, PERIOD, VSEGO_ZADOLJENNOST) AS 
                (
                    SELECT
                        CASE WHEN CREDIT_PROCENT > 20 THEN 5
                            WHEN CREDIT_PROCENT > 15 THEN 4 
                            WHEN CREDIT_PROCENT > 10 THEN 3 
                            WHEN CREDIT_PROCENT > 5 THEN 2 
                            ELSE 1 END AS GROUPS, 
                        UNIQUE_CODE,
                        CLIENT_TYPE,
                        SUBSTR(SROK,1,1),
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS
                    WHERE REPORT_ID = %s AND CODE_VAL <> '000'
                ),

                UL_LONG_TABLE (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE CLIENT_TYPE LIKE 'J' AND PERIOD = 3
                    GROUP BY GROUPS
                ),

                UL_SHORT_TABLE (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE CLIENT_TYPE LIKE 'J' AND PERIOD = 1
                    GROUP BY GROUPS
                ),

                FL_LONG_TABLE (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE CLIENT_TYPE LIKE 'P' AND PERIOD = 3
                    GROUP BY GROUPS
                ),

                FL_SHORT_TABLE (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE CLIENT_TYPE LIKE 'P' AND PERIOD = 1
                    GROUP BY GROUPS
                )	

            SELECT 
                P.GROUPS AS Numeral,
                P.TITLE as Title, 
                NVL(ULL.BALANS,0)/1000000 AS ULLongTerm,
                NVL(ULS.BALANS,0)/1000000 AS ULShortTerm,
                NVL(FLL.BALANS,0)/1000000 AS FLLongTerm,
                NVL(FLS.BALANS,0)/1000000 AS FLShortTerm,
                NVL(ULL.BALANS,0)/S_ULL.TOTAL AS ULLongPart,
                NVL(ULS.BALANS,0)/S_ULS.TOTAL AS ULShortPart,
                NVL(FLL.BALANS,0)/S_FLL.TOTAL AS FLLongPart,
                NVL(FLS.BALANS,0)/S_FLS.TOTAL AS FLShortPart
            FROM VIEW_PERCENTAGE_NAMES P
            LEFT JOIN UL_LONG_TABLE ULL  ON ULL.GROUPS = P.GROUPS
            LEFT JOIN UL_SHORT_TABLE ULS ON ULS.GROUPS = P.GROUPS
            LEFT JOIN FL_LONG_TABLE FLL  ON FLL.GROUPS = P.GROUPS
            LEFT JOIN FL_SHORT_TABLE FLS ON FLS.GROUPS = P.GROUPS,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM UL_LONG_TABLE) S_ULL,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM UL_SHORT_TABLE) S_ULS,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM FL_LONG_TABLE) S_FLL,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM FL_SHORT_TABLE) S_FLS 
            ORDER BY P.GROUPS
        '''

    @staticmethod
    def orcl_bypercentage_national_ul():
        return '''
            WITH                    
                REPORT_DATA_TABLE (GROUPS, TERM, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        CASE WHEN CREDIT_PROCENT > 20 THEN 5
                            WHEN CREDIT_PROCENT > 15 THEN 4 
                            WHEN CREDIT_PROCENT > 10 THEN 3 
                            WHEN CREDIT_PROCENT > 5 THEN 2 
                            ELSE 1 END AS GROUPS,
                        TERM,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS R
                    WHERE REPORT_ID = %s AND CLIENT_TYPE = 'J' AND CODE_VAL = '000'),

                TERMLESS_2 (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 2 OR TERM IS NULL
                    GROUP BY GROUPS
                ),

                TERMLESS_5 (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 5 AND TERM > 2
                    GROUP BY GROUPS
                ),

                TERMLESS_7 (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 7 AND TERM > 5
                    GROUP BY GROUPS
                ),

                TERMLESS_10 (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 10 AND TERM > 7
                    GROUP BY GROUPS
                ),

                TERMMORE_10 (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM > 10
                    GROUP BY GROUPS
                )

            SELECT 
				P.GROUPS AS Numeral,
                P.TITLE as Title,
                NVL(TL2.BALANS,0)/1000000 AS TermLess2,
                NVL(TL5.BALANS,0)/1000000 AS TermLess5,
                NVL(TL7.BALANS,0)/1000000 AS TermLess7,
                NVL(TL10.BALANS,0)/1000000 AS TermLess10,
                NVL(TM10.BALANS,0)/1000000 AS TermMore10,
                NVL(TL2.BALANS,0)/STL2.TOTAL AS PartLess2,
                NVL(TL5.BALANS,0)/STL5.TOTAL AS PartLess5,
                NVL(TL7.BALANS,0)/STL7.TOTAL AS PartLess7,
                NVL(TL10.BALANS,0)/STL10.TOTAL AS PartLess10,
                NVL(TM10.BALANS,0)/STM10.TOTAL AS PartMore10
            FROM VIEW_PERCENTAGE_NAMES P
            LEFT JOIN TERMLESS_2 TL2  ON TL2.GROUPS = P.GROUPS
            LEFT JOIN TERMLESS_5 TL5  ON TL5.GROUPS = P.GROUPS
            LEFT JOIN TERMLESS_7 TL7  ON TL7.GROUPS = P.GROUPS
            LEFT JOIN TERMLESS_10 TL10  ON TL10.GROUPS = P.GROUPS
            LEFT JOIN TERMMORE_10 TM10  ON TM10.GROUPS = P.GROUPS,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM TERMLESS_2) STL2,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM TERMLESS_5) STL5,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM TERMLESS_7) STL7,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM TERMLESS_10) STL10,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM TERMMORE_10) STM10
            ORDER BY P.GROUPS
        '''

    @staticmethod
    def orcl_bypercentage_foreign_ul():
        return '''
            WITH                    
                REPORT_DATA_TABLE (GROUPS, TERM, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        CASE WHEN CREDIT_PROCENT > 20 THEN 5
                            WHEN CREDIT_PROCENT > 15 THEN 4 
                            WHEN CREDIT_PROCENT > 10 THEN 3 
                            WHEN CREDIT_PROCENT > 5 THEN 2 
                            ELSE 1 END AS GROUPS,
                        TERM,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS R
                    WHERE REPORT_ID = %s AND CLIENT_TYPE = 'J' AND CODE_VAL <> '000'),

                TERMLESS_2 (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 2 OR TERM IS NULL
                    GROUP BY GROUPS
                ),

                TERMLESS_5 (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 5 AND TERM > 2
                    GROUP BY GROUPS
                ),

                TERMLESS_7 (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 7 AND TERM > 5
                    GROUP BY GROUPS
                ),

                TERMLESS_10 (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 10 AND TERM > 7
                    GROUP BY GROUPS
                ),

                TERMMORE_10 (GROUPS, BALANS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM > 10
                    GROUP BY GROUPS
                )

            SELECT 
				P.GROUPS AS Numeral,
                P.TITLE as Title,
                NVL(TL2.BALANS,0)/1000000 AS TermLess2,
                NVL(TL5.BALANS,0)/1000000 AS TermLess5,
                NVL(TL7.BALANS,0)/1000000 AS TermLess7,
                NVL(TL10.BALANS,0)/1000000 AS TermLess10,
                NVL(TM10.BALANS,0)/1000000 AS TermMore10,
                NVL(TL2.BALANS,0)/STL2.TOTAL AS PartLess2,
                NVL(TL5.BALANS,0)/STL5.TOTAL AS PartLess5,
                NVL(TL7.BALANS,0)/STL7.TOTAL AS PartLess7,
                NVL(TL10.BALANS,0)/STL10.TOTAL AS PartLess10,
                NVL(TM10.BALANS,0)/STM10.TOTAL AS PartMore10
            FROM VIEW_PERCENTAGE_NAMES P
            LEFT JOIN TERMLESS_2 TL2  ON TL2.GROUPS = P.GROUPS
            LEFT JOIN TERMLESS_5 TL5  ON TL5.GROUPS = P.GROUPS
            LEFT JOIN TERMLESS_7 TL7  ON TL7.GROUPS = P.GROUPS
            LEFT JOIN TERMLESS_10 TL10  ON TL10.GROUPS = P.GROUPS
            LEFT JOIN TERMMORE_10 TM10  ON TM10.GROUPS = P.GROUPS,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM TERMLESS_2) STL2,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM TERMLESS_5) STL5,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM TERMLESS_7) STL7,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM TERMLESS_10) STL10,
            (SELECT NVL(SUM(BALANS),1) AS TOTAL FROM TERMMORE_10) STM10
            ORDER BY P.GROUPS
        '''

    @staticmethod
    def orcl_byaverageweight_ul():
        return '''
            WITH
                REPORT_DATA_TABLE (GROUPS, CURRENCY_NAME, CREDIT_PERCENT, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        CASE WHEN SUBSTR(SROK,1,1) = '3' 
                          THEN 1 ELSE 2 END AS GROUPS,
                        CURRENCY_NAME,
                        CREDIT_PROCENT * VSEGO_ZADOLJENNOST,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS
                    WHERE REPORT_ID = %s AND CLIENT_TYPE = 'J'),

                VALUTA_UZS (GROUPS, AVERAGE) AS (
                    SELECT GROUPS, SUM(CREDIT_PERCENT)/SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE CURRENCY_NAME = 'UZS'
                    GROUP BY GROUPS
                ),

                VALUTA_USD (GROUPS, AVERAGE) AS (
                    SELECT GROUPS, SUM(CREDIT_PERCENT)/SUM(VSEGO_ZADOLJENNOST)
                    FROM REPORT_DATA_TABLE D
                    WHERE CURRENCY_NAME = 'USD'
                    GROUP BY GROUPS
                ),

                VALUTA_EUR (GROUPS, AVERAGE) AS (
                    SELECT GROUPS, SUM(CREDIT_PERCENT)/SUM(VSEGO_ZADOLJENNOST)
                    FROM REPORT_DATA_TABLE D
                    WHERE CURRENCY_NAME = 'EUR'
                    GROUP BY GROUPS
                ),

                VALUTA_JPY (GROUPS, AVERAGE) AS (
                    SELECT GROUPS, SUM(CREDIT_PERCENT)/SUM(VSEGO_ZADOLJENNOST)
                    FROM REPORT_DATA_TABLE D
                    WHERE CURRENCY_NAME = 'JPY'
                    GROUP BY GROUPS
                )

            SELECT 
                TN.GROUPS as id,
                TN.TITLE as Title,
                NVL(UZS.AVERAGE,0) AS AverageUZS,
                NVL(USD.AVERAGE,0) AS AverageUSD,
                NVL(EUR.AVERAGE,0) AS AverageEUR,
                NVL(JPY.AVERAGE,0) AS AverageJPY,
                S_UZS.TOTAL AS TotalUZS,
                S_USD.TOTAL AS TotalUSD,
                S_EUR.TOTAL AS TotalEUR,
                S_JPY.TOTAL AS TotalJPY
            FROM VIEW_TERMTYPE_NAMES TN
            LEFT JOIN VALUTA_UZS UZS  ON UZS.GROUPS = TN.GROUPS
            LEFT JOIN VALUTA_USD USD  ON USD.GROUPS = TN.GROUPS
            LEFT JOIN VALUTA_EUR EUR  ON EUR.GROUPS = TN.GROUPS
            LEFT JOIN VALUTA_JPY JPY  ON JPY.GROUPS = TN.GROUPS,
            (SELECT SUM(CREDIT_PERCENT)/SUM(VSEGO_ZADOLJENNOST) AS TOTAL
              FROM REPORT_DATA_TABLE D WHERE CURRENCY_NAME = 'UZS') S_UZS,
            (SELECT SUM(CREDIT_PERCENT)/SUM(VSEGO_ZADOLJENNOST) AS TOTAL
              FROM REPORT_DATA_TABLE D WHERE CURRENCY_NAME = 'USD') S_USD,
            (SELECT SUM(CREDIT_PERCENT)/SUM(VSEGO_ZADOLJENNOST) AS TOTAL
              FROM REPORT_DATA_TABLE D WHERE CURRENCY_NAME = 'EUR') S_EUR,
            (SELECT SUM(CREDIT_PERCENT)/SUM(VSEGO_ZADOLJENNOST) AS TOTAL
              FROM REPORT_DATA_TABLE D WHERE CURRENCY_NAME = 'JPY') S_JPY
            ORDER BY TN.GROUPS
        '''

    @staticmethod
    def orcl_byaverageweight_fl():
        return '''
            WITH 
                REPORT_DATA (ID, GROUPS, PERCENT, LOANS) AS ( 
                    SELECT ID,
                        VID_KREDITOVANIYA,
                        CREDIT_PROCENT*VSEGO_ZADOLJENNOST,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS
                    WHERE REPORT_ID = %s AND CLIENT_TYPE = 'P'
                )
            SELECT 
                MAX(ID) AS id,
                SUBSTR(GROUPS,4) AS Title, 
                SUM(PERCENT)/SUM(LOANS) AS Balance,
                MAX(S.TOTAL) AS Average
            FROM REPORT_DATA,
            (SELECT SUM(PERCENT)/SUM(LOANS) AS TOTAL FROM REPORT_DATA) S
            GROUP BY GROUPS
        '''

    @staticmethod
    def orcl_npls_by_branches():
        return ''' 
            SELECT 
                MAX(NAME) AS Title, 
                GEOCODE AS GeoCode, 
                SUM(TOTAL_LOAN)/1000000 AS Balance 
            FROM (
                SELECT 
                  MAX(B.NAME) AS NAME, 
                  MAX(B.GEOCODE) AS GEOCODE, 
                  SUM(VSEGO_ZADOLJENNOST) AS TOTAL_LOAN
                FROM CREDITS R
                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                WHERE R.REPORT_ID = %s
                GROUP BY UNIQUE_CODE
                HAVING NVL(MAX(DAYS),0) > 90 
                   AND NVL(MAX(ARREAR_DAYS),0) > 90 
                    OR SUM(OSTATOK_SUDEB) IS NOT NULL 
                    OR SUM(OSTATOK_VNEB_PROSR) IS NOT NULL
                )
            GROUP BY GEOCODE
            ORDER BY BALANCE
        '''

    @staticmethod
    def orcl_toxics_by_branches():
        return '''
            SELECT 
                MAX(NAME) AS Title, 
                GEOCODE AS GeoCode, 
                SUM(TOTAL_LOAN)/1000000 AS Balance 
            FROM (
                SELECT 
                  MAX(B.NAME) AS NAME, 
                  MAX(B.GEOCODE) AS GEOCODE, 
                  SUM(VSEGO_ZADOLJENNOST) AS TOTAL_LOAN
                FROM CREDITS R
                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                WHERE R.REPORT_ID = %s
                GROUP BY UNIQUE_CODE
                HAVING NVL(MAX(DAYS),0) <= 90 
                   AND NVL(MAX(ARREAR_DAYS),0) <= 90 
                    AND SUM(OSTATOK_SUDEB) IS  NULL 
                    AND SUM(OSTATOK_VNEB_PROSR) IS  NULL
                    AND SUM(OSTATOK_PERESM) IS NOT NULL
                )
            GROUP BY GEOCODE
            ORDER BY BALANCE
        '''

    @staticmethod
    def orcl_overdues_by_branches():
        return '''
            SELECT 
                MAX(B.NAME) AS Title,
                B.GEOCODE AS GeoCode,  
                NVL(SUM(OSTATOK_PROSR)/1000000,0) AS Balance
            FROM CREDITS_REPORTDATA R
            LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
            WHERE R.REPORT_ID = %s
            GROUP BY B.GEOCODE
            ORDER BY Balance
        '''
    @staticmethod
    def named_query_byweight_ul():
        return '''
            SELECT CREDIT_PROCENT, VSEGO_ZADOLJENNOST, SROK, C.NAME AS VALUTE, T.NAME AS TYPE_CLIENT
	            FROM credits_reportdata R
	            LEFT JOIN credits_currency C ON C.CODE = R.CODE_VAL
	            LEFT JOIN credits_clienttype T ON T.CODE = R.BALANS_SCHET
	            WHERE T.NAME = 'ЮЛ' AND REPORT_ID = %s;
            '''

    @staticmethod
    def named_query_byweight_fl():
        return '''
            SELECT CREDIT_PROCENT, VSEGO_ZADOLJENNOST, VID_KREDITOVANIYA, SROK, C.NAME AS VALUTE, T.NAME AS TYPE_CLIENT
	            FROM credits_reportdata R
	            LEFT JOIN credits_currency C ON C.CODE = R.CODE_VAL
	            LEFT JOIN credits_clienttype T ON T.CODE = R.BALANS_SCHET
	            WHERE T.NAME = 'ФЛ' AND REPORT_ID = %s;
            '''

    @staticmethod
    def orcl_byoverduebrach():
        return '''
            SELECT 
              B.SORT as id,
              B.NAME as Title,
              C.MFO,
              COUNT(C.ID) AS CountPr,
              SUM(VSEGO_ZADOLJENNOST) AS Balance,
              NVL(SUM(OSTATOK_PROSR),0) AS Overdue
            FROM CREDITS C
            LEFT JOIN CREDITS_BRANCH B ON B.CODE = C.MFO
            WHERE REPORT_ID = %s 
              AND DATE_DOGOVOR >= TO_DATE('2019-12-01', 'YYYY-MM-DD')
            GROUP BY B.NAME, B.SORT, C.MFO

            ORDER BY B.SORT
        '''
