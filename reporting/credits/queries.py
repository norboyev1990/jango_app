class Query():
    def named_query_npls():
        return '''SELECT R.id, 
                        CASE T.SUBJ
                            WHEN 'J' THEN SUBSTR(CREDIT_SCHET,10,8)
                            ELSE SUBSTR(INN_PASSPORT,11,9)
                        END	AS UNIQUE_CODE,
                        NAME_CLIENT AS BORROWER,
                        B.NAME AS BRANCH_NAME,
                        ROUND(SUM(VSEGO_ZADOLJENNOST)/1000000, 2) AS LOAN_BALANCE,
                        JULIANDAY('2020-02-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) AS DAY_COUNT,
                        SUM(OSTATOK_SUDEB) AS SUDEB,
                        SUM(OSTATOK_VNEB_PROSR) AS PROSR
                    FROM CREDITS_REPORTDATA R
                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                    WHERE REPORT_id = %s
                    GROUP BY UNIQUE_CODE
                    HAVING DAY_COUNT > 90 OR SUDEB IS NOT NULL OR PROSR IS NOT NULL 
                    ORDER BY LOAN_BALANCE DESC
                    LIMIT 10
                '''

    def named_query_toxics():
        return '''SELECT R.id, 
                        SUBSTR(CREDIT_SCHET,10,8) AS UNIQUE_CODE, 
                        COUNT(*),
                        NAME_CLIENT AS BORROWER,
                        B.NAME AS BRANCH_NAME,
                        ROUND(SUM(VSEGO_ZADOLJENNOST)/1000000, 2) AS LOAN_BALANCE,
                        JULIANDAY('2020-02-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) AS DAY_COUNT,
                        SUM(OSTATOK_SUDEB) AS SUDEB,
                        SUM(OSTATOK_VNEB_PROSR) AS PROSR,
                        SUM(OSTATOK_PERESM) AS PERESM
                    FROM CREDITS_REPORTDATA R
                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                    WHERE R.REPORT_ID = 82
                    GROUP BY UNIQUE_CODE, NAME_CLIENT
                    HAVING PERESM IS NOT NULL and (DAY_COUNT < 90 or DAY_COUNT IS NULL)  and PROSR IS NULL and SUDEB IS NULL
                    ORDER BY LOAN_BALANCE DESC
                    LIMIT 10
                '''

    def named_query_overdues():
        return '''SELECT R.id, 
                        CASE T.SUBJ
                            WHEN 'J' THEN SUBSTR(CREDIT_SCHET,10,8)
                            ELSE SUBSTR(INN_PASSPORT,11,9)
                        END	AS UNIQUE_CODE,
                        NAME_CLIENT AS BORROWER,
                        B.NAME AS BRANCH_NAME,
                        ROUND(SUM(OSTATOK_NACH_PROSR_PRCNT)/1000000, 2) AS LOAN_BALANCE
                    FROM CREDITS_REPORTDATA R
                    LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                    LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                    WHERE REPORT_id = 82
                    GROUP BY UNIQUE_CODE
                    ORDER BY LOAN_BALANCE DESC
                    LIMIT 10
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

    def named_query_byterms():
        return '''WITH MYVIEW (ID, TERM, VSEGO_ZADOLJENNOST) AS (
                            SELECT ID,
                            CASE WHEN DATE_POGASH_POSLE_PRODL IS NULL 
                                THEN ROUND((JULIANDAY(DATE_POGASH) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                ELSE ROUND((JULIANDAY(DATE_POGASH_POSLE_PRODL) - JULIANDAY(DATE_DOGOVOR))/365,1)
                                END	AS TERM,
                                VSEGO_ZADOLJENNOST
                            FROM credits_reportdata
                            WHERE REPORT_id = 86
                        )
                            
                        SELECT 
                            CASE WHEN TERM <= 2 THEN '1_GROUP_2'
                                WHEN TERM > 2 AND TERM <= 5 THEN '2_GROUP_2_5'
                                WHEN TERM > 5 AND TERM <= 7 THEN '3_GROUP_5_7'
                                WHEN TERM > 7 AND TERM <= 10 THEN '4_GROUP_7_10'
                                ELSE '5_GROUP_10' END AS GROUPS,
                            COUNT(ID) AS COUNT,
                            ROUND(SUM(VSEGO_ZADOLJENNOST)/1000000, 0) AS SUMMA	
                        FROM MYVIEW
                        GROUP BY GROUPS
                        ORDER BY GROUPS DESC
                '''

    def named_query_bysubjects():
        return '''WITH 
                            MAIN_TABLE (GROUPS, TITLE, TOTAL_LOAN) AS (
                                SELECT 
                                    CASE T.NAME 
                                        WHEN 'ЮЛ' THEN 1 
                                        WHEN 'ИП' THEN 2 
                                        ELSE 3 END AS GROUPS,
                                    T.NAME AS TITLE, 
                                    SUM(VSEGO_ZADOLJENNOST)
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86
                                GROUP BY GROUPS),
                                
                            REPORT_DATA_TABLE (GROUPS, VSEGO_ZADOLJENNOST, OSTATOK_REZERV, UNIQUE_CODE) AS (
                                SELECT 
                                    CASE T.NAME 
                                        WHEN 'ЮЛ' THEN 1 
                                        WHEN 'ИП' THEN 2 
                                        ELSE 3 END AS GROUPS,
                                    VSEGO_ZADOLJENNOST, 
                                    OSTATOK_REZERV,
                                    CASE WHEN T.SUBJ = 'J' 
                                    THEN SUBSTR(CREDIT_SCHET,10,8)
                                    ELSE SUBSTR(INN_PASSPORT,11,9) 
                                    END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86),
                                
                            NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID=86 AND (JULIANDAY('2020-04-01') - JULIANDAY(DATE_OBRAZ_PROS) > 90
                                    OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL)
                                GROUP BY UNIQUE_CODE
                            ),

                            NPL_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM NPL_UNIQUE_TABLE NPL
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = NPL.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),

                            TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE R.REPORT_ID = 86
                                GROUP BY UNIQUE_CODE, NAME_CLIENT
                                HAVING 
                                    SUM(OSTATOK_PERESM) IS NOT NULL AND 
                                    SUM(OSTATOK_VNEB_PROSR) IS NULL AND 
                                    SUM(OSTATOK_SUDEB) IS NULL AND (
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) < 90 OR 
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) IS NULL)
                            ),

                            TOX_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM TOX_UNIQUE_TABLE TOX
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = TOX.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),

                            REZ_TABLE (GROUPS, TOTAL_RESERVE) AS (
                                SELECT GROUPS, SUM(OSTATOK_REZERV) 
                                FROM REPORT_DATA_TABLE D
                                GROUP BY GROUPS
                            )

                            SELECT *, 
                            LOAN/TOTALS AS RATION,
                            NPL_LOAN+TOX_LOAN AS TOX_NPL,
                            (NPL_LOAN+TOX_LOAN)/TOTALS AS WEIGHT,
                            RESERVE/(NPL_LOAN+TOX_LOAN) AS COATING
                            FROM (	
                            SELECT 
                                M.TITLE,
                                M.GROUPS,
                                M.TOTAL_LOAN/1000000 AS LOAN,
                                N.TOTAL_LOAN/1000000 AS NPL_LOAN,
                                CASE WHEN T.TOTAL_LOAN IS NOT NULL 
                                    THEN T.TOTAL_LOAN/1000000
                                    ELSE 0 END AS TOX_LOAN,
                                R.TOTAL_RESERVE/1000000 AS RESERVE,
                                (SELECT SUM(TOTAL_LOAN)/1000000 FROM MAIN_TABLE) AS TOTALS
                            FROM MAIN_TABLE M
                            LEFT JOIN NPL_TABLE N ON N.GROUPS = M.GROUPS
                            LEFT JOIN TOX_TABLE T ON T.GROUPS = M.GROUPS
                            LEFT JOIN REZ_TABLE R ON R.GROUPS = M.GROUPS
                            )
                            ORDER BY GROUPS
                '''

    def named_query_bysegments():
        return '''WITH 
                            MAIN_TABLE (GROUPS, TITLE, TOTAL_LOAN) AS (
                                SELECT 
                                    CASE WHEN T.SUBJ = 'J' THEN 
                                        CASE WHEN SUBSTR(OBESPECHENIE,1,2) == '42' 
                                        THEN 1 ELSE 2 END ELSE 3 
                                        END	AS GROUPS,
                                    CASE WHEN T.SUBJ = 'J' THEN 
                                        CASE WHEN SUBSTR(OBESPECHENIE,1,2) == '42' 
                                        THEN 'Инв. проект' ELSE 'ЮЛ' END ELSE 'ФЛ' 
                                        END	AS TITLE,
                                    SUM(VSEGO_ZADOLJENNOST)
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86
                                GROUP BY GROUPS),
                                
                            REPORT_DATA_TABLE (GROUPS, VSEGO_ZADOLJENNOST, OSTATOK_REZERV, UNIQUE_CODE) AS (
                                SELECT 
                                    CASE WHEN T.SUBJ = 'J' THEN 
                                        CASE WHEN SUBSTR(OBESPECHENIE,1,2) == '42' 
                                        THEN 1 ELSE 2 END ELSE 3 
                                        END	AS GROUPS,
                                    VSEGO_ZADOLJENNOST, 
                                    OSTATOK_REZERV,
                                    CASE WHEN T.SUBJ = 'J' 
                                    THEN SUBSTR(CREDIT_SCHET,10,8)
                                    ELSE SUBSTR(INN_PASSPORT,11,9) 
                                    END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86),
                                
                            NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID=86 AND (JULIANDAY('2020-04-01') - JULIANDAY(DATE_OBRAZ_PROS) > 90
                                    OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL)
                                GROUP BY UNIQUE_CODE
                            ),
                            
                            NPL_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM NPL_UNIQUE_TABLE NPL
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = NPL.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),
                            
                            TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE R.REPORT_ID = 86
                                GROUP BY UNIQUE_CODE, NAME_CLIENT
                                HAVING 
                                    SUM(OSTATOK_PERESM) IS NOT NULL AND 
                                    SUM(OSTATOK_VNEB_PROSR) IS NULL AND 
                                    SUM(OSTATOK_SUDEB) IS NULL AND (
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) < 90 OR 
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) IS NULL)
                            ),
                            
                            TOX_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM TOX_UNIQUE_TABLE TOX
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = TOX.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),
                            
                            REZ_TABLE (GROUPS, TOTAL_RESERVE) AS (
                                SELECT GROUPS, SUM(OSTATOK_REZERV) 
                                FROM REPORT_DATA_TABLE D
                                GROUP BY GROUPS
                            )
                            
                        SELECT *, 
                        LOAN/TOTALS AS RATION,
                        NPL_LOAN+TOX_LOAN AS TOX_NPL,
                        (NPL_LOAN+TOX_LOAN)/LOAN AS WEIGHT,
                        RESERVE/(NPL_LOAN+TOX_LOAN) AS COATING
                        FROM (	
                            SELECT 
                                M.TITLE,
                                M.GROUPS,
                                M.TOTAL_LOAN/1000000 AS LOAN,
                                N.TOTAL_LOAN/1000000 AS NPL_LOAN,
                                CASE WHEN T.TOTAL_LOAN IS NOT NULL 
                                    THEN T.TOTAL_LOAN/1000000
                                    ELSE 0 END AS TOX_LOAN,
                                R.TOTAL_RESERVE/1000000 AS RESERVE,
                                (SELECT SUM(TOTAL_LOAN)/1000000 FROM MAIN_TABLE) AS TOTALS
                            FROM MAIN_TABLE M
                            LEFT JOIN NPL_TABLE N ON N.GROUPS = M.GROUPS
                            LEFT JOIN TOX_TABLE T ON T.GROUPS = M.GROUPS
                            LEFT JOIN REZ_TABLE R ON R.GROUPS = M.GROUPS
                        )
                        ORDER BY GROUPS
                '''

    def named_query_bycurrency():
        return '''WITH 
                            MAIN_TABLE (GROUPS, TITLE, TOTAL_LOAN) AS (
                                SELECT 
                                    CASE WHEN CODE_VAL == '000' 
                                        THEN 1 ELSE 2 
                                        END AS GROUPS,
                                    CASE WHEN CODE_VAL == '000' 
                                        THEN 'Национальная валюта'
                                        ELSE 'Иностранная валюта' 
                                        END AS TITLE,
                                    SUM(VSEGO_ZADOLJENNOST)
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86
                                GROUP BY GROUPS),
                                
                            REPORT_DATA_TABLE (GROUPS, VSEGO_ZADOLJENNOST, OSTATOK_REZERV, UNIQUE_CODE) AS (
                                SELECT 
                                    CASE WHEN CODE_VAL == '000' 
                                        THEN 1 ELSE 2 
                                        END AS GROUPS,
                                    VSEGO_ZADOLJENNOST, 
                                    OSTATOK_REZERV,
                                    CASE WHEN T.SUBJ = 'J' 
                                    THEN SUBSTR(CREDIT_SCHET,10,8)
                                    ELSE SUBSTR(INN_PASSPORT,11,9) 
                                    END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86),
                                
                            NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID=86 AND (JULIANDAY('2020-04-01') - JULIANDAY(DATE_OBRAZ_PROS) > 90
                                    OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL)
                                GROUP BY UNIQUE_CODE
                            ),
                            
                            NPL_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM NPL_UNIQUE_TABLE NPL
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = NPL.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),
                            
                            TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE R.REPORT_ID = 86
                                GROUP BY UNIQUE_CODE, NAME_CLIENT
                                HAVING 
                                    SUM(OSTATOK_PERESM) IS NOT NULL AND 
                                    SUM(OSTATOK_VNEB_PROSR) IS NULL AND 
                                    SUM(OSTATOK_SUDEB) IS NULL AND (
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) < 90 OR 
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) IS NULL)
                            ),
                            
                            TOX_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM TOX_UNIQUE_TABLE TOX
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = TOX.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),
                            
                            REZ_TABLE (GROUPS, TOTAL_RESERVE) AS (
                                SELECT GROUPS, SUM(OSTATOK_REZERV) 
                                FROM REPORT_DATA_TABLE D
                                GROUP BY GROUPS
                            )
                            
                        SELECT *, 
                        LOAN/TOTALS AS RATION,
                        NPL_LOAN+TOX_LOAN AS TOX_NPL,
                        (NPL_LOAN+TOX_LOAN)/LOAN AS WEIGHT,
                        RESERVE/(NPL_LOAN+TOX_LOAN) AS COATING
                        FROM (	
                            SELECT 
                                M.TITLE,
                                M.GROUPS,
                                M.TOTAL_LOAN/1000000 AS LOAN,
                                N.TOTAL_LOAN/1000000 AS NPL_LOAN,
                                CASE WHEN T.TOTAL_LOAN IS NOT NULL 
                                    THEN T.TOTAL_LOAN/1000000
                                    ELSE 0 END AS TOX_LOAN,
                                R.TOTAL_RESERVE/1000000 AS RESERVE,
                                (SELECT SUM(TOTAL_LOAN)/1000000 FROM MAIN_TABLE) AS TOTALS
                            FROM MAIN_TABLE M
                            LEFT JOIN NPL_TABLE N ON N.GROUPS = M.GROUPS
                            LEFT JOIN TOX_TABLE T ON T.GROUPS = M.GROUPS
                            LEFT JOIN REZ_TABLE R ON R.GROUPS = M.GROUPS
                        )
                        ORDER BY GROUPS
                '''

    def named_query_bybranches():
        return '''WITH 
                            MAIN_TABLE (GROUPS, TITLE, TOTAL_LOAN) AS (
                                SELECT 
                                    B.SORT AS GROUPS,
                                    B.NAME AS TITLE, 
                                    SUM(VSEGO_ZADOLJENNOST)
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                                WHERE REPORT_ID = 86
                                GROUP BY GROUPS),
                                
                            REPORT_DATA_TABLE (GROUPS, VSEGO_ZADOLJENNOST, OSTATOK_REZERV, UNIQUE_CODE) AS (
                                SELECT 
                                    B.SORT AS GROUPS,
                                    VSEGO_ZADOLJENNOST, 
                                    OSTATOK_REZERV,
                                    CASE WHEN T.SUBJ = 'J' 
                                    THEN SUBSTR(CREDIT_SCHET,10,8)
                                    ELSE SUBSTR(INN_PASSPORT,11,9) 
                                    END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                LEFT JOIN CREDITS_BRANCH B ON B.CODE = R.MFO
                                WHERE REPORT_ID = 86),
                                
                            NPL_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID=86 AND (JULIANDAY('2020-04-01') - JULIANDAY(DATE_OBRAZ_PROS) > 90
                                    OR OSTATOK_SUDEB IS NOT NULL OR OSTATOK_VNEB_PROSR IS NOT NULL)
                                GROUP BY UNIQUE_CODE
                            ),

                            NPL_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM NPL_UNIQUE_TABLE NPL
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = NPL.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),

                            TOX_UNIQUE_TABLE (UNIQUE_CODE) AS (
                                SELECT
                                    CASE T.SUBJ WHEN 'J' 
                                        THEN SUBSTR(CREDIT_SCHET,10,8)
                                        ELSE SUBSTR(INN_PASSPORT,11,9) 
                                        END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE R.REPORT_ID = 86
                                GROUP BY UNIQUE_CODE, NAME_CLIENT
                                HAVING 
                                    SUM(OSTATOK_PERESM) IS NOT NULL AND 
                                    SUM(OSTATOK_VNEB_PROSR) IS NULL AND 
                                    SUM(OSTATOK_SUDEB) IS NULL AND (
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) < 90 OR 
                                    JULIANDAY('2020-04-01') - JULIANDAY(MIN(DATE_OBRAZ_PROS)) IS NULL)
                            ),

                            TOX_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) FROM (
                                    SELECT D.* FROM TOX_UNIQUE_TABLE TOX
                                    LEFT JOIN REPORT_DATA_TABLE D ON D.UNIQUE_CODE = TOX.UNIQUE_CODE)
                                GROUP BY GROUPS
                            ),

                            REZ_TABLE (GROUPS, TOTAL_RESERVE) AS (
                                SELECT GROUPS, SUM(OSTATOK_REZERV) 
                                FROM REPORT_DATA_TABLE D
                                GROUP BY GROUPS
                            )

                            SELECT *, 
                            LOAN/TOTALS AS RATION,
                            NPL_LOAN+TOX_LOAN AS TOX_NPL,
                            (NPL_LOAN+TOX_LOAN)/LOAN AS WEIGHT,
                            RESERVE/(NPL_LOAN+TOX_LOAN) AS COATING
                            FROM (	
                            SELECT 
                                M.TITLE,
                                M.GROUPS,
                                CASE WHEN M.TOTAL_LOAN IS NOT NULL 
                                    THEN M.TOTAL_LOAN/1000000
                                    ELSE 0 END AS LOAN,
                                CASE WHEN N.TOTAL_LOAN IS NOT NULL 
                                    THEN N.TOTAL_LOAN/1000000
                                    ELSE 0 END AS NPL_LOAN,
                                CASE WHEN T.TOTAL_LOAN IS NOT NULL 
                                    THEN T.TOTAL_LOAN/1000000
                                    ELSE 0 END AS TOX_LOAN,
                                CASE WHEN R.TOTAL_RESERVE IS NOT NULL 
                                    THEN R.TOTAL_RESERVE/1000000
                                    ELSE 0 END AS RESERVE,
                                (SELECT SUM(TOTAL_LOAN)/1000000 FROM MAIN_TABLE) AS TOTALS
                            FROM MAIN_TABLE M
                            LEFT JOIN NPL_TABLE N ON N.GROUPS = M.GROUPS
                            LEFT JOIN TOX_TABLE T ON T.GROUPS = M.GROUPS
                            LEFT JOIN REZ_TABLE R ON R.GROUPS = M.GROUPS
                            )
                            ORDER BY GROUPS
                '''

    def named_query_bypercentage_national():
        return '''WITH RECURSIVE
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
                                
                            REPORT_DATA_TABLE (GROUPS, SUBJECT, PERIOD, VSEGO_ZADOLJENNOST, UNIQUE_CODE) AS (
                                SELECT 
                                    CASE WHEN CREDIT_PROCENT > 20 THEN 1
                                        WHEN CREDIT_PROCENT > 15 THEN 2 
                                        WHEN CREDIT_PROCENT > 10 THEN 3 
                                        WHEN CREDIT_PROCENT > 5 THEN 4 
                                        ELSE 5 END AS GROUPS,
                                    T.SUBJ,
                                    SROK,
                                    VSEGO_ZADOLJENNOST, 
                                    CASE WHEN T.SUBJ = 'J' 
                                    THEN SUBSTR(CREDIT_SCHET,10,8)
                                    ELSE SUBSTR(INN_PASSPORT,11,9) 
                                    END	AS UNIQUE_CODE
                                FROM CREDITS_REPORTDATA R
                                LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                                WHERE REPORT_ID = 86 AND CODE_VAL = '000'),

                            UL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '3%'
                                GROUP BY GROUPS
                            ),
                            
                            UL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '1%'
                                GROUP BY GROUPS
                            ),
                            
                            FL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '3%'
                                GROUP BY GROUPS
                            ),
                            
                            FL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                                SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                                FROM REPORT_DATA_TABLE D
                                WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '1%'
                                GROUP BY GROUPS
                            )	
                        SELECT 
                            M.TITLE,
                            M.GROUPS,
                            IFNULL(ULL.TOTAL_LOAN/1000000,0) AS ULL_LOAN,
                            IFNULL(ULS.TOTAL_LOAN/1000000,0) AS ULS_LOAN,
                            IFNULL(FLL.TOTAL_LOAN/1000000,0) AS FLL_LOAN,
                            IFNULL(FLS.TOTAL_LOAN/1000000,0) AS FLS_LOAN
                        FROM MAIN_TABLE M
                        LEFT JOIN UL_LONG_TABLE ULL  ON ULL.GROUPS = M.GROUPS
                        LEFT JOIN UL_SHORT_TABLE ULS ON ULS.GROUPS = M.GROUPS
                        LEFT JOIN FL_LONG_TABLE FLL  ON FLL.GROUPS = M.GROUPS
                        LEFT JOIN FL_SHORT_TABLE FLS ON FLS.GROUPS = M.GROUPS
                        ORDER BY M.GROUPS DESC
                '''

    def named_query_bypercentage_foreign():
        return '''WITH RECURSIVE
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
                        
                    REPORT_DATA_TABLE (GROUPS, SUBJECT, PERIOD, VSEGO_ZADOLJENNOST, UNIQUE_CODE) AS (
                        SELECT 
                            CASE WHEN CREDIT_PROCENT > 20 THEN 1
                                WHEN CREDIT_PROCENT > 15 THEN 2 
                                WHEN CREDIT_PROCENT > 10 THEN 3 
                                WHEN CREDIT_PROCENT > 5 THEN 4 
                                ELSE 5 END AS GROUPS,
                            T.SUBJ,
                            SROK,
                            VSEGO_ZADOLJENNOST, 
                            CASE WHEN T.SUBJ = 'J' 
                            THEN SUBSTR(CREDIT_SCHET,10,8)
                            ELSE SUBSTR(INN_PASSPORT,11,9) 
                            END	AS UNIQUE_CODE
                        FROM CREDITS_REPORTDATA R
                        LEFT JOIN CREDITS_CLIENTTYPE T ON T.CODE = R.BALANS_SCHET
                        WHERE REPORT_ID = 86 AND CODE_VAL <> '000'),

                    UL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                        SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                        FROM REPORT_DATA_TABLE D
                        WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '3%'
                        GROUP BY GROUPS
                    ),
                    
                    UL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                        SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                        FROM REPORT_DATA_TABLE D
                        WHERE SUBJECT LIKE 'J' AND PERIOD LIKE '1%'
                        GROUP BY GROUPS
                    ),
                    
                    FL_LONG_TABLE (GROUPS, TOTAL_LOAN) AS (
                        SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                        FROM REPORT_DATA_TABLE D
                        WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '3%'
                        GROUP BY GROUPS
                    ),
                    
                    FL_SHORT_TABLE (GROUPS, TOTAL_LOAN) AS (
                        SELECT GROUPS, SUM(VSEGO_ZADOLJENNOST) 
                        FROM REPORT_DATA_TABLE D
                        WHERE SUBJECT LIKE 'P' AND PERIOD LIKE '1%'
                        GROUP BY GROUPS
                    )
                SELECT 
                    M.TITLE,
                    M.GROUPS,
                    IFNULL(ULL.TOTAL_LOAN/1000000,0) AS ULL_LOAN,
                    IFNULL(ULS.TOTAL_LOAN/1000000,0) AS ULS_LOAN,
                    IFNULL(FLL.TOTAL_LOAN/1000000,0) AS FLL_LOAN,
                    IFNULL(FLS.TOTAL_LOAN/1000000,0) AS FLS_LOAN
                FROM MAIN_TABLE M
                LEFT JOIN UL_LONG_TABLE ULL  ON ULL.GROUPS = M.GROUPS
                LEFT JOIN UL_SHORT_TABLE ULS ON ULS.GROUPS = M.GROUPS
                LEFT JOIN FL_LONG_TABLE FLL  ON FLL.GROUPS = M.GROUPS
                LEFT JOIN FL_SHORT_TABLE FLS ON FLS.GROUPS = M.GROUPS
                ORDER BY M.GROUPS DESC
        '''

    def named_query_bypercentage_national_ul():
        return '''WITH RECURSIVE
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
                    WHERE T.SUBJ = 'J' AND REPORT_ID = 86 AND CODE_VAL = '000'),

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
                M.TITLE,
                M.GROUPS,
                IFNULL(T2.TOTAL_LOAN/1000000,0) AS T2_LOAN,
                IFNULL(T5.TOTAL_LOAN/1000000,0) AS T5_LOAN,
                IFNULL(T7.TOTAL_LOAN/1000000,0) AS T7_LOAN,
                IFNULL(T10.TOTAL_LOAN/1000000,0) AS T10_LOAN,
                IFNULL(T11.TOTAL_LOAN/1000000,0) AS T11_LOAN
            FROM MAIN_TABLE M
            LEFT JOIN TERMLESS_2 T2  ON T2.GROUPS = M.GROUPS
            LEFT JOIN TERMLESS_5 T5  ON T5.GROUPS = M.GROUPS
            LEFT JOIN TERMLESS_7 T7  ON T7.GROUPS = M.GROUPS
            LEFT JOIN TERMLESS_10 T10  ON T10.GROUPS = M.GROUPS
            LEFT JOIN TERMMORE_10 T11  ON T11.GROUPS = M.GROUPS
            ORDER BY M.GROUPS DESC
        '''

    def named_query_bypercentage_foreign_ul():
        return '''WITH RECURSIVE
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
                    WHERE T.SUBJ = 'J' AND REPORT_ID = 86 AND CODE_VAL <> '000'),

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
                M.TITLE,
                M.GROUPS,
                IFNULL(T2.TOTAL_LOAN/1000000,0) AS T2_LOAN,
                IFNULL(T5.TOTAL_LOAN/1000000,0) AS T5_LOAN,
                IFNULL(T7.TOTAL_LOAN/1000000,0) AS T7_LOAN,
                IFNULL(T10.TOTAL_LOAN/1000000,0) AS T10_LOAN,
                IFNULL(T11.TOTAL_LOAN/1000000,0) AS T11_LOAN
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
                        WHERE REPORT_ID = 86 AND T.SUBJ = 'J'),

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
                WHERE R.REPORT_ID = 86 AND T.SUBJ = 'P'
                GROUP BY VID_KREDITOVANIYA
            '''

    def named_query_byretailproduct():
        return '''
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
