focus_areas_to_skills = '''
    WITH meta AS (
        SELECT 'aws' AS platform_short, 'AWS' AS platform
        UNION ALL SELECT 'gcp' AS platform_short, 'Google Cloud' AS platform
        UNION ALL SELECT 'azure' AS platform_short, 'Microsoft Azure' AS platform
        UNION ALL SELECT 'gsuite' AS platform_short, 'Google Workspace' AS platform
        UNION ALL SELECT 'ms365' AS platform_short, 'Microsoft Office 365' AS platform
    ), ptfa AS (
    -- Products that are not VERIFIED should be unassigned
    SELECT
        product,
        platform, 
        CASE 
            WHEN ptfa.status = 'VERIFIED'
            THEN ptfa.p_group
            ELSE 'Unassigned'         
        END AS p_group,
        CASE 
            WHEN ptfa.status = 'VERIFIED'
            THEN ptfa.focus_area
            ELSE 'Unassigned'         
        END AS focus_area,
        ptfa.support_level
    FROM product_to_focus_area ptfa
    )
    SELECT
        -- Create the focus area id
        CONCAT(
            'cre/fa/', 
            meta.platform_short,
            '/',
            REGEXP_REPLACE(LOWER(fa.focus_area), '[ /]', '_')
        ) AS id,
        CASE 
            WHEN fa.platform = 'Microsoft Azure' THEN fa.platform 
            ELSE 
                CONCAT(
                    meta.platform,
                    ' ',
                    fa.focus_area
                ) 
        END AS name,
        CASE 
            WHEN fa.platform = 'Microsoft Azure' THEN fa.platform 
            ELSE 
                CONCAT(
                    meta.platform,
                    ' ',
                    fa.p_group
                ) 
        END AS practice_area,
        ARRAY_SORT(
            ARRAY_UNION(
                -- Aggregate service tags for Products that match cloud catalog
                ARRAY_AGG(
                    CASE 
                        WHEN 
                            ctfa.support_level = 'PRIMARY' 
                            AND cpt_categories.tag_value IS NOT NULL
                        THEN cpt_categories.tag_value 
                        ELSE NULL 
                    END 
                ),
                -- Aggregate category tags for categories that match cloud catalog
                ARRAY_AGG(
                    CASE 
                        WHEN ctfa.support_level = 'PRIMARY' 
                            AND cpt_services.tag_value IS NOT NULL
                        THEN cpt_services.tag_value 
                        ELSE NULL 
                    END
                )
            )
        ) AS primary_skills,
        ARRAY_SORT(
            ARRAY_UNION(
                -- Aggregate service tags for Products that match cloud catalog
                ARRAY_AGG(
                    CASE 
                        WHEN 
                            ctfa.support_level = 'SECONDARY' 
                            AND cpt_categories.tag_value IS NOT NULL
                        THEN cpt_categories.tag_value 
                        ELSE NULL 
                    END 
                ),
                -- Aggregate category tags for categories that match cloud catalog
                ARRAY_AGG(
                    CASE 
                        WHEN ptfa.support_level = 'SECONDARY' 
                            AND cpt_services.tag_value IS NOT NULL
                        THEN cpt_services.tag_value 
                        ELSE NULL 
                    END
                )
            )
        ) AS secondary_skills,
        ARRAY_SORT(
            -- Capture products and category tags that are mapped to focus area but do not exist in CC
            ARRAY_UNION(
                ARRAY_AGG(
                    CASE 
                        WHEN cpt_categories.tag_value IS NULL
                        THEN ctfa.category_tag 
                        ELSE NULL 
                    END 
                ),
                ARRAY_AGG(
                    CASE 
                        WHEN cpt_services.tag_value IS NULL
                        THEN ptfa.product 
                        ELSE NULL 
                    END
                )
            )
        ) AS exceptions
    FROM focus_areas fa
    JOIN meta ON fa.platform = meta.platform
    JOIN category_to_focus_area ctfa 
        ON fa.platform = ctfa.platform
        AND fa.focus_area = ctfa.focus_area
        AND ctfa.support_level != 'NONE'
    JOIN ptfa
        ON fa.platform = ptfa.platform
        AND fa.focus_area = ptfa.focus_area
    LEFT OUTER JOIN catalog_product_tags cpt_services
        ON fa.platform = cpt_services.platform
        AND ptfa.product = cpt_services.product 
        AND cpt_services.tag_type = 'service'
    LEFT OUTER JOIN catalog_product_tags cpt_categories
        ON fa.platform = cpt_categories.platform
        AND ctfa.category_tag = cpt_categories.tag_value 
        AND cpt_categories.tag_type = 'category'
    GROUP BY 1, 2, 3
    ORDER BY 1
'''

exceptions = '''
    WITH meta AS (
        SELECT 'aws' AS platform_short, 'AWS' AS platform
        UNION ALL SELECT 'gcp' AS platform_short, 'Google Cloud' AS platform
        UNION ALL SELECT 'azure' AS platform_short, 'Microsoft Azure' AS platform
        UNION ALL SELECT 'gsuite' AS platform_short, 'Google Workspace' AS platform
        UNION ALL SELECT 'ms365' AS platform_short, 'Microsoft Office 365' AS platform
    ), ptfa AS (
    -- Products that are not VERIFIED should be unassigned
    SELECT
        product,
        platform, 
        CASE 
            WHEN ptfa.status = 'VERIFIED'
            THEN ptfa.p_group
            ELSE 'Unassigned'         
        END AS p_group,
        CASE 
            WHEN ptfa.status = 'VERIFIED'
            THEN ptfa.focus_area
            ELSE 'Unassigned'         
        END AS focus_area,
        ptfa.support_level
    FROM product_to_focus_area ptfa
    )
    SELECT
        CASE 
            WHEN m.platform IS NOT NULL THEN m.platform
            WHEN ptfa.platform IS NOT NULL THEN ptfa.platform
            WHEN cpt_services.platform IS NOT NULL THEN cpt_services.platform
            WHEN cpt_categories.platform IS NOT NULL THEN cpt_categories.platform
        END as platform,
        ARRAY_COMPACT(
            ARRAY_AGG(
                CASE 
                    WHEN 
                        ptfa.focus_area = 'Unassigned'
                        AND cpt_services.tag_value IS NOT NULL 
                    THEN cpt_services.tag_value 
                    ELSE NULL 
                END
            )
        ) AS unassigned_service_tags,
        ARRAY_COMPACT(
            ARRAY_AGG(
                CASE 
                    WHEN 
                        ctfa.category_tag IS NULL
                        AND cpt_categories.tag_value IS NOT NULL 
                    THEN cpt_categories.tag_value 
                    ELSE NULL 
                END
            )
        ) AS unassigned_category_tags,
        ARRAY_COMPACT(
            ARRAY_AGG(
                CASE 
                    WHEN cpt_services.tag_value IS NULL
                        THEN ptfa.product 
                    ELSE NULL
                END
            ) 
        ) AS products_not_in_catalog,
        ARRAY_COMPACT(
            ARRAY_AGG(
                CASE 
                    WHEN cpt_categories.tag_value IS NULL
                    THEN ctfa.category_tag 
                    ELSE NULL 
                END
            ) 
        ) AS categories_not_in_catalog
    --FROM focus_areas fa
    FROM meta m
    JOIN category_to_focus_area ctfa 
        ON m.platform = ctfa.platform
        AND ctfa.support_level != 'NONE'
    JOIN ptfa
        ON m.platform = ptfa.platform
    FULL OUTER JOIN catalog_product_tags cpt_services
        ON m.platform = cpt_services.platform
        AND ptfa.product = cpt_services.product 
        AND cpt_services.tag_type = 'service'
    FULL OUTER JOIN catalog_product_tags cpt_categories
        ON m.platform = cpt_categories.platform
        AND ctfa.category_tag = cpt_categories.tag_value 
        AND cpt_categories.tag_type = 'category'
    GROUP BY 1
    ORDER BY 1
'''
