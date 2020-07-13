class Query():
    @staticmethod
    def named_query_npls():
        return '''
            SELECT R.ID, 
                ROWNUM AS Number, 
                NAME_CLIENT AS Name,
                B.NAME AS Branch,
                SUM(R.VSEGO_ZADOLJENNOST)/1000000 AS Balans,
                DATE('now','start of year','+'||(L.REPORT_MONTH-1)||' month') AS SDATE
            FROM CREDITS_REPORTDATA R
            LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
            LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
            LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
            WHERE REPORT_ID = %s
            GROUP BY 
                CASE T.SUBJ
                    WHEN 'J' THEN SUBSTR(CREDIT_SCHET,10,8)
                    ELSE SUBSTR(INN_PASSPORT,11,9)
                END
            HAVING 
                JULIANDAY(SDATE) - JULIANDAY(MIN(DATE_OBRAZ_PROS)) > 90 
                OR SUM(OSTATOK_SUDEB) IS NOT NULL 
                OR SUM(OSTATOK_VNEB_PROSR) IS NOT NULL 
            ORDER BY BALANS DESC
        '''

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
            WHERE REPORT_ID = %s
            GROUP BY UNIQUE_CODE
            HAVING 
                extract(day from MIN(L.START_MONTH) - MIN(DATE_OBRAZ_PROS)) > 90
                OR SUM(OSTATOK_SUDEB) IS NOT NULL
                OR SUM(OSTATOK_VNEB_PROSR) IS NOT NULL
            ORDER BY BALANS DESC
        '''

    def named_query_toxics():
        return '''
            SELECT R.ID, 
                ROW_NUMBER () OVER (ORDER BY SUM(VSEGO_ZADOLJENNOST) DESC) AS Number,
                NAME_CLIENT AS Name,
                B.NAME AS Branch,
                SUM(VSEGO_ZADOLJENNOST)/1000000 AS Balans,
                DATE('now','start of year','+'||(L.REPORT_MONTH-1)||' month') AS SDate
            FROM CREDITS_REPORTDATA R
            LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
            LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
            LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
            WHERE R.REPORT_ID = %s
            GROUP BY 
                CASE T.SUBJ
                    WHEN 'J' THEN SUBSTR(CREDIT_SCHET,10,8)
                    ELSE SUBSTR(INN_PASSPORT,11,9)
                END
            HAVING SUM(OSTATOK_PERESM) IS NOT NULL  
                AND SUM(OSTATOK_VNEB_PROSR) IS NULL 
                AND SUM(OSTATOK_SUDEB) IS NULL 
                AND (JULIANDAY(SDATE) - JULIANDAY(MIN(DATE_OBRAZ_PROS)) < 90 
                OR JULIANDAY(SDATE) - JULIANDAY(MIN(DATE_OBRAZ_PROS)) IS NULL
                )
            ORDER BY BALANS DESC
        '''

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
                NVL(extract(day from MIN(L.START_MONTH) - MIN(DATE_OBRAZ_PROS)),0) < 90
                AND SUM(OSTATOK_SUDEB) IS NULL
                AND SUM(OSTATOK_VNEB_PROSR) IS NULL
                AND SUM(OSTATOK_PERESM) IS NOT NULL
            ORDER BY BALANS DESC
        '''

    def named_query_overdues():
        return '''
            SELECT R.ID, 
                ROW_NUMBER () OVER (ORDER BY SUM(OSTATOK_PROSR) DESC) AS Number,
                NAME_CLIENT AS Name,
                B.NAME AS Branch,
                SUM(OSTATOK_PROSR)/1000000 AS Balans
            FROM CREDITS_REPORTDATA R
            LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
            LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
            WHERE REPORT_ID = %s
            GROUP BY 
                CASE T.SUBJ
                    WHEN 'J' THEN SUBSTR(CREDIT_SCHET,10,8)
                    ELSE SUBSTR(INN_PASSPORT,11,9)
                END
            ORDER BY BALANS DESC
                '''

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

    def named_query_indicators():
        return '''WITH NPL_VIEW (REPORT_MONTH, SUMMA_NPL) AS (
                                SELECT REPORT_MONTH, SUM(LOAN_BALANCE) FROM (
                                    SELECT 
                                        L.REPORT_MONTH,
                                        CASE T.SUBJ WHEN 'J' THEN SUBSTR(CREDIT_SCHET,10,8) ELSE SUBSTR(INN_PASSPORT,11,9) END	AS UNIQUE_CODE,
                                        JULIANDAY(DATE('now','start of year','+'||(L.REPORT_MONTH-1)||' month')) - JULIANDAY(MIN(R.DATE_OBRAZ_PROS)) AS DAY_COUNT,
                                        SUM(VSEGO_ZADOLJENNOST) AS LOAN_BALANCE
                                    FROM CREDITS_REPORTDATA R
                                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                    LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                                    LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                                    WHERE L.REPORT_MONTH in (:month2, :month1)
                                    GROUP BY L.REPORT_MONTH, UNIQUE_CODE
                                    HAVING DAY_COUNT > 90 OR SUM(OSTATOK_SUDEB) IS NOT NULL OR SUM(OSTATOK_VNEB_PROSR) IS NOT NULL
                                )
                                GROUP BY REPORT_MONTH
                            ),
                            
                            TOXIC_VIEW (REPORT_MONTH, SUMMA_TOXIC) AS (
                                SELECT REPORT_MONTH, SUM(LOAN_BALANCE) FROM (
                                    SELECT
                                        L.REPORT_MONTH,
                                        CASE T.SUBJ WHEN 'J' THEN SUBSTR(R.CREDIT_SCHET,10,8) ELSE SUBSTR(R.INN_PASSPORT,11,9) END AS UNIQUE_CODE,
                                        JULIANDAY(DATE('now','start of year','+'||(L.REPORT_MONTH-1)||' month')) - JULIANDAY(MIN(R.DATE_OBRAZ_PROS)) AS DAY_COUNT,
                                        SUM(R.VSEGO_ZADOLJENNOST) AS LOAN_BALANCE
                                    FROM CREDITS_REPORTDATA R
                                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                    LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                                    WHERE L.REPORT_MONTH in (:month2, :month1)
                                    GROUP BY L.REPORT_MONTH, UNIQUE_CODE
                                    HAVING SUM(R.OSTATOK_PERESM) IS NOT NULL AND (DAY_COUNT < 90 OR DAY_COUNT IS NULL)  
                                    AND SUM(R.OSTATOK_VNEB_PROSR) IS NULL AND SUM(R.OSTATOK_SUDEB) IS NULL
                                )
                                GROUP BY REPORT_MONTH
                            )
                        SELECT RD.id, 
                            L.REPORT_MONTH, 
                            SUM(VSEGO_ZADOLJENNOST)                 AS CREDIT,
                            N.SUMMA_NPL                             AS NPL, 
                            N.SUMMA_NPL / SUM(VSEGO_ZADOLJENNOST)   AS NPL_WEIGHT,
                            T.SUMMA_TOXIC                           AS TOXIC,
                            T.SUMMA_TOXIC / SUM(VSEGO_ZADOLJENNOST) AS TOXIC_WEIGHT,
                            T.SUMMA_TOXIC + N.SUMMA_NPL             AS TOXIC_NPL,
                            SUM(OSTATOK_REZERV)                     AS RESERVE,
                            SUM(OSTATOK_REZERV) / (T.SUMMA_TOXIC + N.SUMMA_NPL) AS RESERVE_COATING,
                            SUM(OSTATOK_PROSR)                      AS OVERDUE,
                            SUM(OSTATOK_PROSR) / SUM(VSEGO_ZADOLJENNOST) AS OVERDUE_WEIGHT
                        FROM CREDITS_REPORTDATA RD
                        LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = RD.REPORT_ID
                        LEFT JOIN NPL_VIEW N ON N.REPORT_MONTH = L.REPORT_MONTH
                        LEFT JOIN TOXIC_VIEW T ON T.REPORT_MONTH = L.REPORT_MONTH
                        WHERE L.REPORT_MONTH in (:month2, :month1)
                        GROUP BY L.REPORT_MONTH
                '''

    def orcl_byterms():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, DAYS, OSTATOK_SUDEB, 
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
                    WHERE DAYS > 90 OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL
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
                    WHERE OSTATOK_PERESM IS NOT NULL AND (DAYS < 90 OR DAYS IS NULL) 
                        AND OSTATOK_SUDEB IS NULL AND OSTATOK_VNEB_PROSR IS NULL
                    GROUP BY UNIQUE_CODE
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

    def named_query_byterms():
        return '''
            WITH RECURSIVE
                MAIN_TABLE (GROUPS, TITLE) AS (
                    SELECT 1, 'свыше 10 лет'
                    UNION
                    SELECT GROUPS + 1,
                        CASE GROUPS +1
                            WHEN 2 THEN 'от 7-ми до 10 лет' 
                            WHEN 3 THEN 'от 5-ти до 7 лет' 
                            WHEN 4 THEN 'от 2-х до 5 лет' 
                            ELSE 'до 2-х лет' END AS TITLE	
                    FROM MAIN_TABLE LIMIT 5),
                    
                REPORT_DATA_TABLE (
                    GROUPS, UNIQUE_CODE, DAYS, OSTATOK_SUDEB, 
                    OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        CASE WHEN TERM > 10 THEN 1
                            WHEN TERM > 7 AND TERM <= 10 THEN 2
                            WHEN TERM > 5 AND TERM <= 7 THEN 3
                            WHEN TERM > 2 AND TERM <= 5 THEN 4
                            ELSE 5 END AS GROUPS, 
                        CASE SUBJ WHEN 'J' 
                                THEN SUBSTR(CREDIT_SCHET,10,8)
                                ELSE SUBSTR(INN_PASSPORT,11,9) 
                                END	AS UNIQUE_CODE,
                        DAYCOUNT,
                        OSTATOK_SUDEB, 
                        OSTATOK_VNEB_PROSR,
                        OSTATOK_PERESM,
                        OSTATOK_REZERV,
                        VSEGO_ZADOLJENNOST
                    FROM (
                        SELECT *,
                            CASE WHEN DATE_POGASH_POSLE_PRODL IS NULL 
                                THEN ROUND((JULIANDAY(DATE_POGASH) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                ELSE ROUND((JULIANDAY(DATE_POGASH_POSLE_PRODL) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                END	AS TERM,
                            JULIANDAY(L.START_MONTH) - JULIANDAY(DATE_OBRAZ_PROS) AS DAYCOUNT
                        FROM CREDITS_REPORTDATA R
                        LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                        LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                        WHERE REPORT_ID = %s
                    ) T
                ),
                    
                PORTFOLIO_TABLE (GROUPS, BALANS, TOTALS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST),
                    (SELECT SUM(VSEGO_ZADOLJENNOST) FROM CREDITS_REPORTDATA WHERE REPORT_ID=%s) AS TOTALS
                    FROM REPORT_DATA_TABLE
                    GROUP BY GROUPS
                ),

                NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    WHERE DAYS > 90 OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL
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
                ),
                
                RES_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(OSTATOK_REZERV)
                    FROM REPORT_DATA_TABLE D
                    GROUP BY GROUPS
                )
            SELECT 
                M.GROUPS AS id,
                M.Title AS Title,
                IFNULL(P.BALANS/1000000,0) AS PorBalans,
                IFNULL(P.BALANS*100/P.TOTALS,0) AS PorPercent,
                IFNULL(N.BALANS/1000000,0) AS NplBalans,
                IFNULL(T.BALANS/1000000,0) AS ToxBalans,
                IFNULL(R.BALANS/1000000,0) AS ResBalans,
                IFNULL((N.BALANS+T.BALANS)/1000000,0) AS NplToxic
            FROM MAIN_TABLE M
            LEFT JOIN PORTFOLIO_TABLE P  ON P.GROUPS = M.GROUPS
            LEFT JOIN NPL_TABLE N  ON N.GROUPS = M.GROUPS
            LEFT JOIN TOX_TABLE T  ON T.GROUPS = M.GROUPS
            LEFT JOIN RES_TABLE R  ON R.GROUPS = M.GROUPS
            ORDER BY M.GROUPS
        '''

    def named_query_bysubjects():
        return '''
            WITH RECURSIVE
                MAIN_TABLE (GROUPS, TITLE) AS (
                    SELECT 1, 'ЮЛ' UNION
                    SELECT GROUPS + 1, CASE GROUPS +1 
					WHEN 2 THEN 'ИП' ELSE 'ФЛ' END AS TITLE	
                    FROM MAIN_TABLE LIMIT 3),
                    
                REPORT_DATA_TABLE (
                    GROUPS, UNIQUE_CODE, DAYS, OSTATOK_SUDEB, 
                    OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        CASE T.NAME 
							WHEN 'ЮЛ' THEN 1 
							WHEN 'ИП' THEN 2 ELSE 3 END AS GROUPS, 
                        CASE T.SUBJ WHEN 'J' 
							THEN SUBSTR(CREDIT_SCHET,10,8) 
                            ELSE SUBSTR(INN_PASSPORT,11,9) 
							END AS UNIQUE_CODE,
                        JULIANDAY(L.START_MONTH) - JULIANDAY(DATE_OBRAZ_PROS),
                        OSTATOK_SUDEB, 
                        OSTATOK_VNEB_PROSR,
                        OSTATOK_PERESM,
                        OSTATOK_REZERV,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS_REPORTDATA R
					LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                    WHERE REPORT_ID = %s
                ),
                    
                PORTFOLIO_TABLE (GROUPS, BALANS, TOTALS) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST),
                    (SELECT SUM(VSEGO_ZADOLJENNOST) FROM CREDITS_REPORTDATA WHERE REPORT_ID=%s) AS TOTALS
                    FROM REPORT_DATA_TABLE
                    GROUP BY GROUPS
                ),

                NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    WHERE DAYS > 90 OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL
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
                    WHERE OSTATOK_PERESM IS NOT NULL AND (DAYS < 90 OR DAYS IS NULL) 
                        AND OSTATOK_SUDEB IS NULL AND OSTATOK_VNEB_PROSR IS NULL
                    GROUP BY UNIQUE_CODE
                ),
                
                TOX_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM TOX_UNIQUE_TABLE T
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = T.UNIQUE_CODE
                    GROUP BY GROUPS
                ),
                
                RES_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(OSTATOK_REZERV)
                    FROM REPORT_DATA_TABLE D
                    GROUP BY GROUPS
                )
            SELECT 
                M.GROUPS AS id,
                M.Title AS Title,
                IFNULL(P.BALANS/1000000,0) AS PorBalans,
                IFNULL(P.BALANS*100/P.TOTALS,0) AS PorPercent,
                IFNULL(N.BALANS/1000000,0) AS NplBalans,
                IFNULL(T.BALANS/1000000,0) AS ToxBalans,
                IFNULL(R.BALANS/1000000,0) AS ResBalans
            FROM MAIN_TABLE M
            LEFT JOIN PORTFOLIO_TABLE P  ON P.GROUPS = M.GROUPS
            LEFT JOIN NPL_TABLE N  ON N.GROUPS = M.GROUPS
            LEFT JOIN TOX_TABLE T  ON T.GROUPS = M.GROUPS
            LEFT JOIN RES_TABLE R  ON R.GROUPS = M.GROUPS
            ORDER BY M.GROUPS
        '''

    def orcl_bysubjects():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, DAYS, OSTATOK_SUDEB, 
                OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS 
                (
                    SELECT
                        CASE SUBJECT 
                        WHEN TRANSLATE('ЮЛ' USING nchar_cs) THEN 1 
                        WHEN TRANSLATE('ИП' USING nchar_cs) THEN 2 
                        ELSE 3 END AS GROUPS, 
                        CREDITS.UNIQUE_CODE,
                        DAYS,
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
                    WHERE DAYS > 90 OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL
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
                    WHERE OSTATOK_PERESM IS NOT NULL AND (DAYS < 90 OR DAYS IS NULL) 
                        AND OSTATOK_SUDEB IS NULL AND OSTATOK_VNEB_PROSR IS NULL
                    GROUP BY UNIQUE_CODE
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

    def named_query_bysegments():
        return '''
            WITH RECURSIVE       
                REPORT_DATA_TABLE (
                    GROUPS,	TITLE, UNIQUE_CODE, DAYS, OSTATOK_SUDEB, 
                    OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        CASE WHEN T.SUBJ = 'J' THEN 
							CASE WHEN SUBSTR(OBESPECHENIE,1,2) == '42' 
							THEN 1 ELSE 2 END ELSE 3 
							END	AS GROUPS,
						CASE WHEN T.SUBJ = 'J' THEN 
							CASE WHEN SUBSTR(OBESPECHENIE,1,2) == '42' 
							THEN 'Инв. проект' ELSE 'ЮЛ' END ELSE 'ФЛ' 
							END	AS TITLE,
                        CASE T.SUBJ WHEN 'J' 
							THEN SUBSTR(CREDIT_SCHET,10,8)
                            ELSE SUBSTR(INN_PASSPORT,11,9) 
							END AS UNIQUE_CODE,
                        JULIANDAY(L.START_MONTH) - JULIANDAY(DATE_OBRAZ_PROS),
                        OSTATOK_SUDEB, 
                        OSTATOK_VNEB_PROSR,
                        OSTATOK_PERESM,
                        OSTATOK_REZERV,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS_REPORTDATA R
					LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                    WHERE REPORT_ID = %s
                ),
                    
                PORTFOLIO_TABLE (GROUPS, TITLE, BALANS, TOTALS) AS (
                    SELECT GROUPS, TITLE, SUM(VSEGO_ZADOLJENNOST),
                    (SELECT SUM(VSEGO_ZADOLJENNOST) FROM CREDITS_REPORTDATA WHERE REPORT_ID=%s) AS TOTALS
                    FROM REPORT_DATA_TABLE
                    GROUP BY GROUPS
                ),

                NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    WHERE DAYS > 90 OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL
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
                    WHERE OSTATOK_PERESM IS NOT NULL AND (DAYS < 90 OR DAYS IS NULL) 
                        AND OSTATOK_SUDEB IS NULL AND OSTATOK_VNEB_PROSR IS NULL
                    GROUP BY UNIQUE_CODE
                ),
                
                TOX_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM TOX_UNIQUE_TABLE T
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = T.UNIQUE_CODE
                    GROUP BY GROUPS
                ),
                
                RES_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(OSTATOK_REZERV)
                    FROM REPORT_DATA_TABLE D
                    GROUP BY GROUPS
                )
            SELECT 
                P.GROUPS AS id,
                P.Title AS Title,
                IFNULL(P.BALANS/1000000,0) AS PorBalans,
                IFNULL(P.BALANS*100/P.TOTALS,0) AS PorPercent,
                IFNULL(N.BALANS/1000000,0) AS NplBalans,
                IFNULL(T.BALANS/1000000,0) AS ToxBalans,
                IFNULL(R.BALANS/1000000,0) AS ResBalans
            FROM PORTFOLIO_TABLE P
            LEFT JOIN NPL_TABLE N  ON N.GROUPS = P.GROUPS
            LEFT JOIN TOX_TABLE T  ON T.GROUPS = P.GROUPS
            LEFT JOIN RES_TABLE R  ON R.GROUPS = P.GROUPS
            ORDER BY P.GROUPS
        '''

    def orcl_bysegments():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, DAYS, OSTATOK_SUDEB, 
                OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS 
                (
                    SELECT
                        SEGMENT AS GROUPS, 
                        CREDITS.UNIQUE_CODE,
                        DAYS,
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
                    WHERE DAYS > 90 OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL
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
                    WHERE OSTATOK_PERESM IS NOT NULL AND (DAYS < 90 OR DAYS IS NULL) 
                        AND OSTATOK_SUDEB IS NULL AND OSTATOK_VNEB_PROSR IS NULL
                    GROUP BY UNIQUE_CODE
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

    def named_query_bycurrency():
        return '''
            WITH RECURSIVE  
                REPORT_DATA_TABLE (
                    GROUPS,	TITLE, UNIQUE_CODE, DAYS, OSTATOK_SUDEB, 
                    OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        CASE WHEN CODE_VAL == '000' 
							THEN 1 ELSE 2 
							END AS GROUPS,
						CASE WHEN CODE_VAL == '000' 
							THEN 'Национальная валюта'
							ELSE 'Иностранная валюта' 
							END AS TITLE,
                        CASE T.SUBJ WHEN 'J' 
							THEN SUBSTR(CREDIT_SCHET,10,8)
                            ELSE SUBSTR(INN_PASSPORT,11,9) 
							END AS UNIQUE_CODE,
                        JULIANDAY(L.START_MONTH) - JULIANDAY(DATE_OBRAZ_PROS),
                        OSTATOK_SUDEB, 
                        OSTATOK_VNEB_PROSR,
                        OSTATOK_PERESM,
                        OSTATOK_REZERV,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS_REPORTDATA R
					LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                    WHERE REPORT_ID = %s
                ),
                    
                PORTFOLIO_TABLE (GROUPS, TITLE, BALANS, TOTALS) AS (
                    SELECT GROUPS, TITLE, SUM(VSEGO_ZADOLJENNOST),
                    (SELECT SUM(VSEGO_ZADOLJENNOST) FROM CREDITS_REPORTDATA WHERE REPORT_ID=%s) AS TOTALS
                    FROM REPORT_DATA_TABLE
                    GROUP BY GROUPS
                ),

                NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    WHERE DAYS > 90 OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL
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
                    WHERE OSTATOK_PERESM IS NOT NULL AND (DAYS < 90 OR DAYS IS NULL) 
                        AND OSTATOK_SUDEB IS NULL AND OSTATOK_VNEB_PROSR IS NULL
                    GROUP BY UNIQUE_CODE
                ),
                
                TOX_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM TOX_UNIQUE_TABLE T
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = T.UNIQUE_CODE
                    GROUP BY GROUPS
                ),
                
                RES_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(OSTATOK_REZERV)
                    FROM REPORT_DATA_TABLE D
                    GROUP BY GROUPS
                )
            SELECT 
                P.GROUPS AS id,
                P.Title AS Title,
                IFNULL(P.BALANS/1000000,0) AS PorBalans,
                IFNULL(P.BALANS*100/P.TOTALS,0) AS PorPercent,
                IFNULL(N.BALANS/1000000,0) AS NplBalans,
                IFNULL(T.BALANS/1000000,0) AS ToxBalans,
                IFNULL(R.BALANS/1000000,0) AS ResBalans
            FROM PORTFOLIO_TABLE P
            LEFT JOIN NPL_TABLE N  ON N.GROUPS = P.GROUPS
            LEFT JOIN TOX_TABLE T  ON T.GROUPS = P.GROUPS
            LEFT JOIN RES_TABLE R  ON R.GROUPS = P.GROUPS
            ORDER BY P.GROUPS
        '''

    def orcl_bycurrency():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, DAYS, OSTATOK_SUDEB, 
                OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS 
                (
                    SELECT
                        CURRENCY AS GROUPS, 
                        CREDITS.UNIQUE_CODE,
                        DAYS,
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
                    WHERE DAYS > 90 OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL
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
                    WHERE OSTATOK_PERESM IS NOT NULL AND (DAYS < 90 OR DAYS IS NULL) 
                        AND OSTATOK_SUDEB IS NULL AND OSTATOK_VNEB_PROSR IS NULL
                    GROUP BY UNIQUE_CODE
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

    def named_query_bybranches():
        return '''
            WITH RECURSIVE  
                REPORT_DATA_TABLE (
                    GROUPS,	TITLE, UNIQUE_CODE, DAYS, OSTATOK_SUDEB, 
                    OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        B.SORT AS GROUPS,
                        B.NAME AS TITLE,
                        CASE T.SUBJ WHEN 'J' 
							THEN SUBSTR(CREDIT_SCHET,10,8)
                            ELSE SUBSTR(INN_PASSPORT,11,9) 
							END AS UNIQUE_CODE,
                        JULIANDAY(L.START_MONTH) - JULIANDAY(DATE_OBRAZ_PROS),
                        OSTATOK_SUDEB, 
                        OSTATOK_VNEB_PROSR,
                        OSTATOK_PERESM,
                        OSTATOK_REZERV,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS_REPORTDATA R
					LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
					LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                    WHERE REPORT_ID = %s
                ),
                    
                PORTFOLIO_TABLE (GROUPS, TITLE, BALANS, TOTALS) AS (
                    SELECT GROUPS, TITLE, SUM(VSEGO_ZADOLJENNOST),
                    (SELECT SUM(VSEGO_ZADOLJENNOST) FROM CREDITS_REPORTDATA WHERE REPORT_ID=%s) AS TOTALS
                    FROM REPORT_DATA_TABLE
                    GROUP BY GROUPS
                ),

                NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    WHERE DAYS > 90 OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL
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
                    WHERE OSTATOK_PERESM IS NOT NULL AND (DAYS < 90 OR DAYS IS NULL) 
                        AND OSTATOK_SUDEB IS NULL AND OSTATOK_VNEB_PROSR IS NULL
                    GROUP BY UNIQUE_CODE
                ),
                
                TOX_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM TOX_UNIQUE_TABLE T
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = T.UNIQUE_CODE
                    GROUP BY GROUPS
                ),
                
                RES_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(OSTATOK_REZERV)
                    FROM REPORT_DATA_TABLE D
                    GROUP BY GROUPS
                )
            SELECT 
                P.GROUPS AS id,
                P.Title AS Title,
                IFNULL(P.BALANS/1000000,0) AS PorBalans,
                IFNULL(P.BALANS*100/P.TOTALS,0) AS PorPercent,
                IFNULL(N.BALANS/1000000,0) AS NplBalans,
                IFNULL(T.BALANS/1000000,0) AS ToxBalans,
                IFNULL(R.BALANS/1000000,0) AS ResBalans
            FROM PORTFOLIO_TABLE P
            LEFT JOIN NPL_TABLE N  ON N.GROUPS = P.GROUPS
            LEFT JOIN TOX_TABLE T  ON T.GROUPS = P.GROUPS
            LEFT JOIN RES_TABLE R  ON R.GROUPS = P.GROUPS
            ORDER BY P.GROUPS
        '''

    def orcl_bybranches():
        return '''
            WITH 
                REPORT_DATA_TABLE (GROUPS, UNIQUE_CODE, DAYS, OSTATOK_SUDEB, 
                OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS 
                (
                    SELECT
                        BRANCH_SORT AS GROUPS, 
                        CREDITS.UNIQUE_CODE,
                        DAYS,
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
                    WHERE DAYS > 90 OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL
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
                    WHERE OSTATOK_PERESM IS NOT NULL AND (DAYS < 90 OR DAYS IS NULL) 
                        AND OSTATOK_SUDEB IS NULL AND OSTATOK_VNEB_PROSR IS NULL
                    GROUP BY UNIQUE_CODE
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

    def named_query_bypercentage_national():
        return '''
            WITH RECURSIVE
                MAIN_TABLE (GROUPS, TITLE) AS (
                    SELECT 1, '20 и более'
                    UNION
                    SELECT GROUPS + 1,
                        CASE GROUPS +1
                            WHEN 2 THEN '16 - 20' 
                            WHEN 3 THEN '11 - 15' 
                            WHEN 4 THEN '6 - 10' 
                            ELSE '0 - 5' END AS TITLE	
                    FROM MAIN_TABLE LIMIT 5),
                    
                REPORT_DATA_TABLE (GROUPS, SUBJECT, PERIOD, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        CASE WHEN CREDIT_PROCENT > 20 THEN 1
                            WHEN CREDIT_PROCENT > 15 THEN 2 
                            WHEN CREDIT_PROCENT > 10 THEN 3 
                            WHEN CREDIT_PROCENT > 5 THEN 4 
                            ELSE 5 END AS GROUPS,
                        T.SUBJ,
                        SROK,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS_REPORTDATA R
                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    WHERE REPORT_ID = %s AND CODE_VAL = '000'),

                UL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '3%%'
                    GROUP BY GROUPS
                ),
                
                UL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '1%%'
                    GROUP BY GROUPS
                ),
                
                FL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '3%%'
                    GROUP BY GROUPS
                ),
                
                FL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '1%%'
                    GROUP BY GROUPS
                )	
            SELECT 
                M.GROUPS AS id,
                ROW_NUMBER () OVER (ORDER BY M.GROUPS DESC) AS Number,
                M.TITLE AS Title,
                IFNULL(ULL.TOTAL_LOAN/1000000,0) AS ULLongTerm,
                IFNULL(ULS.TOTAL_LOAN/1000000,0) AS ULShortTerm,
                IFNULL(FLL.TOTAL_LOAN/1000000,0) AS FLLongTerm,
                IFNULL(FLS.TOTAL_LOAN/1000000,0) AS FLShortTerm,
                IFNULL(ULL.TOTAL_LOAN*100/(SELECT SUM(TOTAL_LOAN) FROM UL_LONG_TABLE),0) AS ULLongPart,
                IFNULL(ULS.TOTAL_LOAN*100/(SELECT SUM(TOTAL_LOAN) FROM UL_SHORT_TABLE),0) AS ULShortPart,
                IFNULL(FLL.TOTAL_LOAN*100/(SELECT SUM(TOTAL_LOAN) FROM FL_LONG_TABLE),0) AS FLLongPart,
                IFNULL(FLS.TOTAL_LOAN*100/(SELECT SUM(TOTAL_LOAN) FROM FL_SHORT_TABLE),0) AS FLShortPart
            FROM MAIN_TABLE M
            LEFT JOIN UL_LONG_TABLE ULL  ON ULL.GROUPS = M.GROUPS
            LEFT JOIN UL_SHORT_TABLE ULS ON ULS.GROUPS = M.GROUPS
            LEFT JOIN FL_LONG_TABLE FLL  ON FLL.GROUPS = M.GROUPS
            LEFT JOIN FL_SHORT_TABLE FLS ON FLS.GROUPS = M.GROUPS
            ORDER BY M.GROUPS DESC
        '''

    def named_query_bypercentage_foreign():
        return '''
            WITH RECURSIVE
                MAIN_TABLE (GROUPS, TITLE) AS (
                    SELECT 1, '20 и более'
                    UNION
                    SELECT GROUPS + 1,
                        CASE GROUPS +1
                            WHEN 2 THEN '16 - 20' 
                            WHEN 3 THEN '11 - 15' 
                            WHEN 4 THEN '6 - 10' 
                            ELSE '0 - 5' END AS TITLE	
                    FROM MAIN_TABLE LIMIT 5),
                    
                REPORT_DATA_TABLE (GROUPS, SUBJECT, PERIOD, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        CASE WHEN CREDIT_PROCENT > 20 THEN 1
                            WHEN CREDIT_PROCENT > 15 THEN 2 
                            WHEN CREDIT_PROCENT > 10 THEN 3 
                            WHEN CREDIT_PROCENT > 5 THEN 4 
                            ELSE 5 END AS GROUPS,
                        T.SUBJ,
                        SROK,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS_REPORTDATA R
                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    WHERE REPORT_ID = %s AND CODE_VAL <> '000'),

                UL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '3%%'
                    GROUP BY GROUPS
                ),
                
                UL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '1%%'
                    GROUP BY GROUPS
                ),
                
                FL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '3%%'
                    GROUP BY GROUPS
                ),
                
                FL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '1%%'
                    GROUP BY GROUPS
                )	
            SELECT 
                M.GROUPS AS id,
                ROW_NUMBER () OVER (ORDER BY M.GROUPS DESC) AS Number,
                M.TITLE AS Title,
                IFNULL(ULL.TOTAL_LOAN/1000000,0) AS ULLongTerm,
                IFNULL(ULS.TOTAL_LOAN/1000000,0) AS ULShortTerm,
                IFNULL(FLL.TOTAL_LOAN/1000000,0) AS FLLongTerm,
                IFNULL(FLS.TOTAL_LOAN/1000000,0) AS FLShortTerm,
                IFNULL(ULL.TOTAL_LOAN*100/(SELECT SUM(TOTAL_LOAN) FROM UL_LONG_TABLE),0) AS ULLongPart,
                IFNULL(ULS.TOTAL_LOAN*100/(SELECT SUM(TOTAL_LOAN) FROM UL_SHORT_TABLE),0) AS ULShortPart,
                IFNULL(FLL.TOTAL_LOAN*100/(SELECT SUM(TOTAL_LOAN) FROM FL_LONG_TABLE),0) AS FLLongPart,
                IFNULL(FLS.TOTAL_LOAN*100/(SELECT SUM(TOTAL_LOAN) FROM FL_SHORT_TABLE),0) AS FLShortPart
            FROM MAIN_TABLE M
            LEFT JOIN UL_LONG_TABLE ULL  ON ULL.GROUPS = M.GROUPS
            LEFT JOIN UL_SHORT_TABLE ULS ON ULS.GROUPS = M.GROUPS
            LEFT JOIN FL_LONG_TABLE FLL  ON FLL.GROUPS = M.GROUPS
            LEFT JOIN FL_SHORT_TABLE FLS ON FLS.GROUPS = M.GROUPS
            ORDER BY M.GROUPS DESC
        '''

    def named_query_bypercentage_national_ul():
        return '''
            WITH RECURSIVE
                MAIN_TABLE (GROUPS, TITLE) AS (
                    SELECT 1, '20 и более'
                    UNION
                    SELECT GROUPS + 1,
                        CASE GROUPS +1
                            WHEN 2 THEN '16 - 20' 
                            WHEN 3 THEN '11 - 15' 
                            WHEN 4 THEN '6 - 10' 
                            ELSE '0 - 5' END AS TITLE	
                    FROM MAIN_TABLE LIMIT 5),
                    
                REPORT_DATA_TABLE (GROUPS, TERM, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        CASE WHEN CREDIT_PROCENT > 20 THEN 1
                            WHEN CREDIT_PROCENT > 15 THEN 2 
                            WHEN CREDIT_PROCENT > 10 THEN 3 
                            WHEN CREDIT_PROCENT > 5 THEN 4 
                            ELSE 5 END AS GROUPS,
                        CASE WHEN DATE_POGASH_POSLE_PRODL IS NULL 
                            THEN ROUND((JULIANDAY(DATE_POGASH) - JULIANDAY(DATE_DOGOVOR))/365,1)
                            ELSE ROUND((JULIANDAY(DATE_POGASH_POSLE_PRODL) - JULIANDAY(DATE_DOGOVOR))/365,1)
                            END	AS TERM,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS_REPORTDATA R
                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    WHERE T.SUBJ = 'J' AND REPORT_ID = %s AND CODE_VAL = '000'),

                TERMLESS_2 (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 2 OR TERM IS NULL
                    GROUP BY GROUPS
                ),
                
                TERMLESS_5 (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 5 AND TERM > 2
                    GROUP BY GROUPS
                ),
                
                TERMLESS_7 (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 7 AND TERM > 5
                    GROUP BY GROUPS
                ),
                
                TERMLESS_10 (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 10 AND TERM > 7
                    GROUP BY GROUPS
                ),
                
                TERMMORE_10 (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM > 10
                    GROUP BY GROUPS
                )

            SELECT 
				M.GROUPS AS id,
                ROW_NUMBER () OVER (ORDER BY M.GROUPS DESC) AS Number,
                M.TITLE AS Title ,
                IFNULL(T2.TOTAL_LOAN/1000000,0) AS Term1,
                IFNULL(T5.TOTAL_LOAN/1000000,0) AS Term2,
                IFNULL(T7.TOTAL_LOAN/1000000,0) AS Term3,
                IFNULL(T10.TOTAL_LOAN/1000000,0) AS Term4,
                IFNULL(T11.TOTAL_LOAN/1000000,0) AS Term5
            FROM MAIN_TABLE M
            LEFT JOIN TERMLESS_2 T2  ON T2.GROUPS = M.GROUPS
            LEFT JOIN TERMLESS_5 T5  ON T5.GROUPS = M.GROUPS
            LEFT JOIN TERMLESS_7 T7  ON T7.GROUPS = M.GROUPS
            LEFT JOIN TERMLESS_10 T10  ON T10.GROUPS = M.GROUPS
            LEFT JOIN TERMMORE_10 T11  ON T11.GROUPS = M.GROUPS
            ORDER BY M.GROUPS DESC
        '''

    def named_query_bypercentage_foreign_ul():
        return '''
            WITH RECURSIVE
                MAIN_TABLE (GROUPS, TITLE) AS (
                    SELECT 1, '20 и более'
                    UNION
                    SELECT GROUPS + 1,
                        CASE GROUPS +1
                            WHEN 2 THEN '16 - 20' 
                            WHEN 3 THEN '11 - 15' 
                            WHEN 4 THEN '6 - 10' 
                            ELSE '0 - 5' END AS TITLE	
                    FROM MAIN_TABLE LIMIT 5),
                    
                REPORT_DATA_TABLE (GROUPS, TERM, VSEGO_ZADOLJENNOST) AS (
                    SELECT 
                        CASE WHEN CREDIT_PROCENT > 20 THEN 1
                            WHEN CREDIT_PROCENT > 15 THEN 2 
                            WHEN CREDIT_PROCENT > 10 THEN 3 
                            WHEN CREDIT_PROCENT > 5 THEN 4 
                            ELSE 5 END AS GROUPS,
                        CASE WHEN DATE_POGASH_POSLE_PRODL IS NULL 
                            THEN ROUND((JULIANDAY(DATE_POGASH) - JULIANDAY(DATE_DOGOVOR))/365,1)
                            ELSE ROUND((JULIANDAY(DATE_POGASH_POSLE_PRODL) - JULIANDAY(DATE_DOGOVOR))/365,1)
                            END	AS TERM,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS_REPORTDATA R
                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    WHERE T.SUBJ = 'J' AND REPORT_ID = %s AND CODE_VAL <> '000'),

                TERMLESS_2 (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 2 OR TERM IS NULL
                    GROUP BY GROUPS
                ),
                
                TERMLESS_5 (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 5 AND TERM > 2
                    GROUP BY GROUPS
                ),
                
                TERMLESS_7 (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 7 AND TERM > 5
                    GROUP BY GROUPS
                ),
                
                TERMLESS_10 (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM <= 10 AND TERM > 7
                    GROUP BY GROUPS
                ),
                
                TERMMORE_10 (GROUPS, TOTAL_LOAN) AS (
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                    FROM REPORT_DATA_TABLE D
                    WHERE TERM > 10
                    GROUP BY GROUPS
                )

            SELECT 
				M.GROUPS AS id,
                ROW_NUMBER () OVER (ORDER BY M.GROUPS DESC) AS Number,
                M.TITLE AS Title ,
                IFNULL(T2.TOTAL_LOAN/1000000,0) AS Term1,
                IFNULL(T5.TOTAL_LOAN/1000000,0) AS Term2,
                IFNULL(T7.TOTAL_LOAN/1000000,0) AS Term3,
                IFNULL(T10.TOTAL_LOAN/1000000,0) AS Term4,
                IFNULL(T11.TOTAL_LOAN/1000000,0) AS Term5
            FROM MAIN_TABLE M
            LEFT JOIN TERMLESS_2 T2  ON T2.GROUPS = M.GROUPS
            LEFT JOIN TERMLESS_5 T5  ON T5.GROUPS = M.GROUPS
            LEFT JOIN TERMLESS_7 T7  ON T7.GROUPS = M.GROUPS
            LEFT JOIN TERMLESS_10 T10  ON T10.GROUPS = M.GROUPS
            LEFT JOIN TERMMORE_10 T11  ON T11.GROUPS = M.GROUPS
            ORDER BY M.GROUPS DESC
        '''

    def named_query_byaverageweight_ul():
        return '''WITH
                    MAIN_TABLE (GROUPS, TITLE) AS (
                        SELECT 1, 'Долгосрочные'
                        UNION
                        SELECT 2, 'Краткосрочные'
                    ),
                        
                    REPORT_DATA_TABLE (GROUPS, NAME_VALUTA, SUM_CREDIT, VSEGO_ZADOLJENNOST) AS (
                        SELECT 
                            CASE WHEN SUBSTR(SROK,1,1) = '3' 
                                THEN 1 ELSE 2 END AS GROUPS,
                            C.NAME,
                            CREDIT_PROCENT * VSEGO_ZADOLJENNOST,
                            VSEGO_ZADOLJENNOST
                        FROM CREDITS_REPORTDATA R
                        LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                        LEFT JOIN CREDITS_CURRENCY C ON C.CODE = R.CODE_VAL
                        WHERE REPORT_ID = %s AND T.SUBJ = 'J'),

                    VALUTA_UZS (GROUPS, AVERAGE) AS (
                        SELECT GROUPS, SUM(SUM_CREDIT)/SUM(VSEGO_ZADOLJENNOST) 
                        FROM REPORT_DATA_TABLE D
                        WHERE NAME_VALUTA = 'UZS'
                        GROUP BY GROUPS
                    ),
                    
                    VALUTA_USD (GROUPS, AVERAGE) AS (
                        SELECT GROUPS, SUM(SUM_CREDIT)/SUM(VSEGO_ZADOLJENNOST)
                        FROM REPORT_DATA_TABLE D
                        WHERE NAME_VALUTA = 'USD'
                        GROUP BY GROUPS
                    ),
                    
                    VALUTA_EUR (GROUPS, AVERAGE) AS (
                        SELECT GROUPS, SUM(SUM_CREDIT)/SUM(VSEGO_ZADOLJENNOST)
                        FROM REPORT_DATA_TABLE D
                        WHERE NAME_VALUTA = 'EUR'
                        GROUP BY GROUPS
                    ),
                    
                    VALUTA_JPY (GROUPS, AVERAGE) AS (
                        SELECT GROUPS, SUM(SUM_CREDIT)/SUM(VSEGO_ZADOLJENNOST)
                        FROM REPORT_DATA_TABLE D
                        WHERE NAME_VALUTA = 'JPY'
                        GROUP BY GROUPS
                    )

                SELECT 
                    M.TITLE,
                    M.GROUPS,
                    IFNULL(UZS.AVERAGE,0) AS UZS_AVERAGE,
                    IFNULL(USD.AVERAGE,0) AS USD_AVERAGE,
                    IFNULL(EUR.AVERAGE,0) AS EUR_AVERAGE,
                    IFNULL(JPY.AVERAGE,0) AS JPY_AVERAGE
                FROM MAIN_TABLE M
                LEFT JOIN VALUTA_UZS UZS  ON UZS.GROUPS = M.GROUPS
                LEFT JOIN VALUTA_USD USD  ON USD.GROUPS = M.GROUPS
                LEFT JOIN VALUTA_EUR EUR  ON EUR.GROUPS = M.GROUPS
                LEFT JOIN VALUTA_JPY JPY  ON JPY.GROUPS = M.GROUPS
                ORDER BY M.GROUPS
            '''

    def named_query_byaverageweight_fl():
        return '''SELECT VID_KREDITOVANIYA AS TITLE, 
                    ROUND(SUM(CREDIT_PROCENT*VSEGO_ZADOLJENNOST)/SUM(VSEGO_ZADOLJENNOST),1) AS BALANS,
                    SUM(CREDIT_PROCENT*VSEGO_ZADOLJENNOST) CREDIT,
                    SUM(VSEGO_ZADOLJENNOST) LOAN
                FROM CREDITS_REPORTDATA R
                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                WHERE R.REPORT_ID = %s AND T.SUBJ = 'P'
                GROUP BY VID_KREDITOVANIYA
            '''

    def named_query_byretailproduct():
        return '''
            WITH 	
                REPORT_DATA_TABLE (ID,
                    GROUPS, UNIQUE_CODE, DAYS, OSTATOK_SUDEB, OSTATOK_PROSR,OSTATOK_NACH_PRCNT,
                    OSTATOK_VNEB_PROSR, OSTATOK_PERESM, OSTATOK_REZERV, VSEGO_ZADOLJENNOST) AS (
                    SELECT R.ID,
                        VID_KREDITOVANIYA,
                        CASE SUBJ WHEN 'J' 
                                THEN SUBSTR(CREDIT_SCHET,10,8)
                                ELSE SUBSTR(INN_PASSPORT,11,9) 
                                END	AS UNIQUE_CODE,
                        JULIANDAY(L.START_MONTH) - JULIANDAY(DATE_OBRAZ_PROS),
                        OSTATOK_SUDEB, 
                        OSTATOK_PROSR,
                        OSTATOK_NACH_PRCNT,
                        OSTATOK_VNEB_PROSR,
                        OSTATOK_PERESM,
                        OSTATOK_REZERV,
                        VSEGO_ZADOLJENNOST
                    FROM CREDITS_REPORTDATA R
                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                        LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                        WHERE REPORT_ID = %s 
                            AND VID_KREDITOVANIYA IN (
                                '30-Потребительский кредит', 
                                '32-Микрозаем', 
                                '34-Автокредит', 
                                '54-Овердрафт по пластиковым карточкам физических лиц', 
                                '59-Образовательный кредит'
                            )
                ),
                    
                PORTFOLIO_TABLE (ID, GROUPS, BALANS, TOTALS, PROSR, NACHPROSR) AS (
                    SELECT ID, GROUPS, SUM(VSEGO_ZADOLJENNOST),
                        (SELECT SUM(VSEGO_ZADOLJENNOST) FROM CREDITS_REPORTDATA WHERE REPORT_ID=%s 
                        AND VID_KREDITOVANIYA IN (
                                '30-Потребительский кредит', 
                                '32-Микрозаем', 
                                '34-Автокредит', 
                                '54-Овердрафт по пластиковым карточкам физических лиц', 
                                '59-Образовательный кредит'
                            )
                        ) AS TOTALS,
                        SUM(OSTATOK_PROSR),
                        SUM(OSTATOK_NACH_PRCNT)
                    FROM REPORT_DATA_TABLE
                    GROUP BY GROUPS
                ),

                NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                    SELECT UNIQUE_CODE
                    FROM REPORT_DATA_TABLE R
                    WHERE DAYS > 90 OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL
                    GROUP BY UNIQUE_CODE
                ),
                
                NPL_TABLE (GROUPS, BALANS) AS(
                    SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST)
                    FROM NPL_UNIQUE_TABLE N
                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = N.UNIQUE_CODE
                    GROUP BY GROUPS
                )
            SELECT P.ID as id,
                ROW_NUMBER () OVER (ORDER BY P.GROUPS) AS Number,
                P.GROUPS AS Title,
                IFNULL(P.BALANS/1000000,0) AS PorBalans,
                IFNULL(P.BALANS*100/P.TOTALS,0) AS PorPercent,
                IFNULL(P.PROSR/1000000,0) AS PrsBalans,
                IFNULL(N.BALANS/1000000,0) AS NplBalans,
                IFNULL(N.BALANS*100/P.BALANS,0) AS NplWeight,
                IFNULL(P.NACHPROSR/1000000,0) AS NachBalans
            FROM PORTFOLIO_TABLE P
            LEFT JOIN NPL_TABLE N  ON N.GROUPS = P.GROUPS
            ORDER BY P.GROUPS
        '''

    def named_query_contracts():
        return '''SELECT 
                CODE_CONTRACT AS id,
                NAME_CLIENT,
                DATE_DOGOVOR,
                DATE_POGASH,
                SUM_DOG_NOM,
                C.NAME AS VALUTE,
                B.NAME AS BRANCH,
                T.NAME AS TYPE_CLIENT
            --S.NAME AS SEGMENT 
            FROM credits_reportdata R
            LEFT JOIN credits_currency C ON C.CODE = R.CODE_VAL
            LEFT JOIN credits_branch B ON B.CODE = R.MFO
            LEFT JOIN credits_clienttype T ON T.CODE = R.BALANS_SCHET
            --LEFT JOIN credits_segment S ON S.CODE = CAST(SUBSTR(R.OTRASL_KREDITOVANIYA,1,2) AS INTEGER)
            GROUP BY CODE_CONTRACT
            HAVING TYPE_CLIENT LIKE 'ЮЛ'
            ORDER BY CODE_CONTRACT
        
        '''

    def named_query_npls_by_branches():
        return '''
            SELECT 
                ID AS id, 
                NAME AS Title, 
                GEOCODE AS GeoCode, 
                SUM(TOTAL_LOAN)/1000000 AS Balance 
            FROM (
                SELECT R.ID, B.NAME, B.GEOCODE, 
                    SUM(VSEGO_ZADOLJENNOST) AS TOTAL_LOAN,
                    DATE('now','start of year','+'||(L.REPORT_MONTH-1)||' month') AS SDate
                FROM CREDITS_REPORTDATA R
                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                WHERE R.REPORT_ID = %s
                GROUP BY CASE T.SUBJ WHEN 'J' THEN SUBSTR(R.CREDIT_SCHET,10,8) ELSE SUBSTR(R.INN_PASSPORT,11,9) END
                HAVING JULIANDAY(SDATE) - JULIANDAY(MIN(DATE_OBRAZ_PROS)) > 90 
                    OR SUM(OSTATOK_SUDEB) IS NOT NULL 
                    OR SUM(OSTATOK_VNEB_PROSR) IS NOT NULL
                )
            GROUP BY GEOCODE
            ORDER BY BALANCE
        '''

    def named_query_toxics_by_branches():
        return '''
            SELECT 
                ID AS id, 
                NAME AS Title, 
                GEOCODE AS GeoCode, 
                CAST(IFNULL(SUM(TOTAL_LOAN)/1000000,0) AS INTEGER) AS Balance 
            FROM (
                SELECT R.ID, B.NAME, B.GEOCODE, 
                    SUM(VSEGO_ZADOLJENNOST) AS TOTAL_LOAN,
                    DATE('now','start of year','+'||(L.REPORT_MONTH-1)||' month') AS SDate
                FROM CREDITS_REPORTDATA R
                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                LEFT JOIN CREDITS_LISTREPORTS L ON L.ID = R.REPORT_ID
                WHERE R.REPORT_ID = %s
                GROUP BY CASE T.SUBJ WHEN 'J' THEN SUBSTR(R.CREDIT_SCHET,10,8) ELSE SUBSTR(R.INN_PASSPORT,11,9) END
                HAVING SUM(OSTATOK_PERESM) IS NOT NULL  
                    AND SUM(OSTATOK_VNEB_PROSR) IS NULL 
                    AND SUM(OSTATOK_SUDEB) IS NULL 
                    AND (JULIANDAY(SDATE) - JULIANDAY(MIN(DATE_OBRAZ_PROS)) < 90 
                    OR JULIANDAY(SDATE) - JULIANDAY(MIN(DATE_OBRAZ_PROS)) IS NULL
                    )
                )
            GROUP BY GEOCODE
            ORDER BY BALANCE
        '''

    def named_query_overdues_by_branches():
        return '''
            SELECT 
                R.ID AS id, 
                B.NAME AS Title,
                B.GEOCODE AS GeoCode,  
                IFNULL(SUM(OSTATOK_PROSR)/1000000,0) AS Balance
            FROM CREDITS_REPORTDATA R
            LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
            WHERE R.REPORT_ID = %s
            GROUP BY B.GEOCODE
            ORDER BY Balance
        '''

    def named_query_byweight_ul():
        return '''
            SELECT CREDIT_PROCENT, VSEGO_ZADOLJENNOST, SROK, C.NAME AS VALUTE, T.NAME AS TYPE_CLIENT
	            FROM credits_reportdata R
	            LEFT JOIN credits_currency C ON C.CODE = R.CODE_VAL
	            LEFT JOIN credits_clienttype T ON T.CODE = R.BALANS_SCHET
	            WHERE TYPE_CLIENT = 'ЮЛ' AND REPORT_ID = %s;
            '''

    def named_query_byweight_fl():
        return '''
            SELECT CREDIT_PROCENT, VSEGO_ZADOLJENNOST, VID_KREDITOVANIYA, SROK, C.NAME AS VALUTE, T.NAME AS TYPE_CLIENT
	            FROM credits_reportdata R
	            LEFT JOIN credits_currency C ON C.CODE = R.CODE_VAL
	            LEFT JOIN credits_clienttype T ON T.CODE = R.BALANS_SCHET
	            WHERE TYPE_CLIENT = 'ФЛ' AND REPORT_ID = %s;
            '''

    def named_query_insert():
        return '''INTO CREDITS_TEMPDATA (
                ID, MONTH_CODE, NUMBERS, CODE_REG, MFO,NAME_CLIENT, BALANS_SCHET, CREDIT_SCHET, DATE_RESHENIYA,
                CODE_VAL, SUM_DOG_NOM, SUM_DOG_EKV, DATE_DOGOVOR, DATE_FACTUAL, DATE_POGASH,
                SROK, DOG_NUMBER_DATE, CREDIT_PROCENT, PROSR_PROCENT, OSTATOK_CRED_SCHET,
                OSTATOK_PERESM, DATE_PRODL, DATE_POGASH_POSLE_PRODL, OSTATOK_PROSR,
                DATE_OBRAZ_PROS, OSTATOK_SUDEB, KOD_PRAVOXR_ORG, PRIZNAK_RESHENIYA,
                DATE_PRED_RESH, VSEGO_ZADOLJENNOST, CLASS_KACHESTVA, OSTATOK_REZERV,
                OSTATOK_NACH_PRCNT, OSTATOK_NACH_PROSR_PRCNT, OCENKA_OBESPECHENIYA,
                OBESPECHENIE, OPISANIE_OBESPECHENIE, ISTOCHNIK_SREDTSVO, VID_KREDITOVANIYA,
                PURPOSE_CREDIT, VISHEST_ORG_CLIENT, OTRASL_KREDITOVANIYA, OTRASL_CLIENTA,
                CLASS_KREDIT_SPOS, PREDSEDATEL_KB, ADRESS_CLIENT, UN_NUMBER_CONTRACT,
                INN_PASSPORT, OSTATOK_VNEB_PROSR, KONKR_NAZN_CREDIT, BORROWER_TYPE,
                SVYAZANNIY, MALIY_BIZNES, REGISTER_NUMBER, OKED,CODE_CONTRACT) 
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
        '''

    def named_query_insert_month():
        return '''INSERT ALL 
                INTO CREDITS_TEMPDATA (MONTH_CODE) VALUES (%s)
                INTO CREDITS_TEMPDATA (MONTH_CODE) VALUES (%s)
            SELECT * FROM dual
        '''
