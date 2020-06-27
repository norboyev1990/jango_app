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