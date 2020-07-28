class Query:
    @staticmethod
    def report_top():
        return """
        SELECT 
            CR.UNIQUE_CODE,
            MAX(CR.NAME) TITLE,
            MAX(CR.TOTAL_LOAN) PORTFEL,
            T.PERIOD_2,
            SUM(CASE T.CODE_VAL 
                WHEN TRANSLATE('840' USING nchar_cs) THEN T.PROGNOZ_POGASH*10173.28
                WHEN TRANSLATE('978' USING nchar_cs) THEN T.PROGNOZ_POGASH*11411.48
                WHEN TRANSLATE('392' USING nchar_cs) THEN T.PROGNOZ_POGASH*94.89
                ELSE T.PROGNOZ_POGASH END) TOTAL,
            SUM(CASE T.CODE_VAL  WHEN TRANSLATE('000' USING nchar_cs) 
                THEN T.PROGNOZ_POGASH ELSE 0 END) NATIONAL
        FROM (
            SELECT 
                UNIQUE_CODE,
                MFO,
                MAX(NAME_CLIENT) AS NAME,
                SUM(VSEGO_ZADOLJENNOST) TOTAL_LOAN
            FROM CREDITS
            WHERE REPORT_ID = 7
            GROUP BY UNIQUE_CODE, MFO
            HAVING SUM(VSEGO_ZADOLJENNOST) IS NOT NULL
            ORDER BY TOTAL_LOAN DESC
            FETCH NEXT 25 ROWS ONLY) CR
        LEFT JOIN VIEW1 T ON T.MFO = CR.MFO AND T.UNIKAL = CR.UNIQUE_CODE
        GROUP BY CR.UNIQUE_CODE, T.PERIOD_2
        ORDER BY PORTFEL DESC, T.PERIOD_2
        """

    @staticmethod
    def report_all():
        return """
        SELECT A.*, 
            CASE SCHET 
                WHEN 1 THEN 'Государственным предприятиям'
                WHEN 2 THEN 'Физическим лицам'
                ELSE 'Частные предприятиям'
            END TITLE,
            PL.NAME
        FROM (
            SELECT SCHET, PERIOD_1, IS_NATIONAL, 
                SUM(CASE CODE_VAL 
                    WHEN TRANSLATE('840' USING nchar_cs) THEN PROGNOZ_POGASH*10173.28
                    WHEN TRANSLATE('978' USING nchar_cs) THEN PROGNOZ_POGASH*11411.48
                    WHEN TRANSLATE('392' USING nchar_cs) THEN PROGNOZ_POGASH*94.89
                    ELSE PROGNOZ_POGASH END) TOTAL 
            FROM VIEW1
            GROUP BY SCHET, PERIOD_1, IS_NATIONAL
            ORDER BY SCHET, PERIOD_1, IS_NATIONAL) A
        LEFT JOIN PAYMENTS_PERIODLIST1 PL ON PL.CODE = A.PERIOD_1
        """

    @staticmethod
    def report_by_client():
        return """
        SELECT IS_FL, PERIOD_2,
            CASE IS_FL 
                WHEN 1 THEN 'ФЛ'
                ELSE 'ЮЛ'
            END TITLE, 
            SUM(CASE CODE_VAL 
                WHEN TRANSLATE('840' USING nchar_cs) THEN PROGNOZ_POGASH*10173.28
                WHEN TRANSLATE('978' USING nchar_cs) THEN PROGNOZ_POGASH*11411.48
                WHEN TRANSLATE('392' USING nchar_cs) THEN PROGNOZ_POGASH*94.89
                ELSE PROGNOZ_POGASH END)/1000000 TOTAL,
            SUM(CASE CODE_VAL 
                WHEN TRANSLATE('840' USING nchar_cs) THEN PROGNOZ_POGASH*10173.28
                WHEN TRANSLATE('978' USING nchar_cs) THEN PROGNOZ_POGASH*11411.48
                WHEN TRANSLATE('392' USING nchar_cs) THEN PROGNOZ_POGASH*94.89
                ELSE 0 END)/1000000 NATION
        FROM VIEW1
        GROUP BY IS_FL, PERIOD_2
        ORDER BY IS_FL, PERIOD_2
        """
        
    @staticmethod
    def report_by_currency():
        return """
        SELECT SCHET, PERIOD_1, 
        CASE SCHET 
                WHEN 1 THEN 'Государственным предприятиям'
                WHEN 2 THEN 'Физическим лицам'
                ELSE 'Частные предприятиям'
            END TITLE,
        SUM(PROGNOZ_POGASH) TOTAL 
        FROM VIEW1
        WHERE CODE_VAL = %s
        GROUP BY SCHET, PERIOD_1
        ORDER BY SCHET, PERIOD_1
        """
