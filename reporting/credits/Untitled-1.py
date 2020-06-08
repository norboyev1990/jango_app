printf("%.2f", SUM(RD.OSTATOK_NACH_PROSR_PRCNT / 1000000)) AS LOAN_BALANCE,

WITH RECURSIVE 
                parent_of(id, unique_code) as (
                    select cre.id, substr(cre.credit_schet,10,8) unique_code from credits_reportdata cre
                    left join credits_clienttype ct on cre.balans_schet = ct.code
                    where ct.subj = 'j' and ( julianday('2020-01-01') - julianday(cre.date_obraz_pros) > 90
                        or cre.ostatok_sudeb is not null or cre.ostatok_vneb_prosr is not null)
                    union all
                    select cr.id, substr(cr.credit_schet,10,8) from credits_reportdata cr, parent_of
                    where substr(cr.credit_schet,10,8) = parent_of.unique_code
                )
                SELECT RD.*
                FROM parent_of p
                LEFT JOIN CREDITS_REPORTDATA RD ON RD.ID = p.id
