class Query():
    def findClients():
        return '''
            SELECT 
                CASE T.SUBJ WHEN 'J' THEN SUBSTR(R.INN_PASSPORT,1,9) 
                ELSE SUBSTR(R.INN_PASSPORT,11,9) END AS ClientID,
                R.NAME_CLIENT AS ClientName,
                T.NAME AS ClientType,
                SUM(R.VSEGO_ZADOLJENNOST) AS TotalLoans,
                R.ADRESS_CLIENT AS Address
            from credits_reportdata R
            LEFT JOIN credits_clienttype T ON T.CODE = R.BALANS_SCHET
            WHERE REPORT_id = %s
            GROUP BY ClientID
            HAVING ClientID <>'' AND T.SUBJ = 'J'
        '''
    def findClientByID():
        return '''
            SELECT *,
                COUNT(*) AS CountLoans, 
                SUM(VSEGO_ZADOLJENNOST)  AS TotalLoans,
                substr(ADRESS_CLIENT, 1, pos-1) AS Address,
                substr(ADRESS_CLIENT, pos+1) AS Phone
            FROM (
                SELECT 
                    CASE T.SUBJ WHEN 'J' THEN SUBSTR(R.INN_PASSPORT,1,9) 
                    ELSE SUBSTR(R.INN_PASSPORT,11,9) END AS ClientID,
                    R.NAME_CLIENT AS ClientName,
                    CASE T.NAME 
                        WHEN 'ЮЛ' THEN 'ЮРИДИЧЕСКОЕ ЛИЦА'
                        WHEN 'ИП' THEN 'ИНДИВИДУАЛНОЕ ПРЕДПРИЯТИЯ'
                        ELSE 'ФИЗИЧЕСКОЕ ЛИЦА' END AS ClientType,
                    R.VSEGO_ZADOLJENNOST ,
                    CASE instr(R.ADRESS_CLIENT,',') WHEN 0 THEN 999 ELSE instr(R.ADRESS_CLIENT,',') END  AS POS,
                    R.ADRESS_CLIENT
                from credits_reportdata R
                LEFT JOIN credits_clienttype T ON T.CODE = R.BALANS_SCHET
                WHERE REPORT_id=86
                )
            WHERE ClientID LIKE %s
            GROUP BY ClientID



        '''