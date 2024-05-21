focus_areas_to_skills_sql = '''
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
        ) AS secondary_skills
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
        AND ptfa.product = cpt_services.name 
        AND cpt_services.tag_type = 'service'
    LEFT OUTER JOIN catalog_product_tags cpt_categories
        ON fa.platform = cpt_categories.platform
        AND ctfa.category_tag = cpt_categories.tag_value 
        AND cpt_categories.tag_type = 'category'
    GROUP BY 1, 2, 3
    ORDER BY 1
'''

exceptions_sql = '''
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
            ptfa.support_level,
            CASE 
                WHEN 
                    STARTSWITH(support_level_desc, 'SUGGESTED Focus Area')
                THEN 
                    REPLACE(support_level_desc, 'SUGGESTED Focus Area', CONCAT('SUGGESTED Focus Area: ', ptfa.focus_area))
                WHEN 
                    STARTSWITH(support_level_desc, 'Does not meet')
                THEN 
                    CONCAT('Unassigned, ', support_level_desc)
                ELSE support_level_desc
            END AS support_level_desc
        FROM product_to_focus_area ptfa
    ), mappings_by_platform AS (
        SELECT
            meta.platform, 
            ARRAY_SORT(
                ARRAY_COMPACT(
                    ARRAY_UNION(
                    -- Aggregate service tags for Products that match cloud catalog
                        ARRAY_AGG(
                            CASE 
                                WHEN 
                                    ctfa.support_level IN ('PRIMARY', 'SECONDARY') 
                                    AND cpt_categories.tag_value IS NOT NULL
                                THEN cpt_categories.tag_value 
                                ELSE NULL 
                            END 
                        ),
                        -- Aggregate category tags for categories that match cloud catalog
                        ARRAY_AGG(
                            CASE 
                                WHEN ctfa.support_level IN ('PRIMARY', 'SECONDARY')
                                    AND cpt_services.tag_value IS NOT NULL
                                THEN cpt_services.tag_value 
                                ELSE NULL 
                            END
                        )
                    )
                )
            ) AS mapped_skills,
            ARRAY_SORT(
                -- Capture products and category tags that are mapped to focus area but do not exist in CC
                ARRAY_DISTINCT(
                    ARRAY_COMPACT(
                        ARRAY_AGG(
                            CASE 
                                WHEN cpt_services.tag_value IS NULL
                                THEN ptfa.product 
                                ELSE NULL 
                            END
                        )
                    )
                )
            ) AS product_exceptions
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
            AND ptfa.product = cpt_services.name 
            AND cpt_services.tag_type = 'service'
        LEFT OUTER JOIN catalog_product_tags cpt_categories
            ON fa.platform = cpt_categories.platform
            AND ctfa.category_tag = cpt_categories.tag_value 
            AND cpt_categories.tag_type = 'category'
        GROUP BY 1
        ORDER BY 1
    ), catalog_by_platform( 
        SELECT 
            m.platform as platform,
            ARRAY_COMPACT(
                ARRAY_DISTINCT(
                    ARRAY_AGG(cpt.tag_value)
                )
            ) AS tag_values
        FROM meta m
        JOIN catalog_product_tags cpt
            ON m.platform = cpt.platform
            AND cpt.tag_type IN ('service', 'category')
        GROUP BY 1
    ), platform_exceptions_agg (
        SELECT 
            m.platform,
            ARRAY_SORT(
                ARRAY_COMPACT(
                    ARRAY_DISTINCT(
                        ARRAY_EXCEPT(c.tag_values, m.mapped_skills)
                    )
                )
            ) AS tag_values,
            m.product_exceptions as products_without_service_tags
        FROM mappings_by_platform m
        JOIN catalog_by_platform c 
            ON m.platform = c.platform
    ), platform_exceptions_exploded (
        SELECT platform, EXPLODE(tag_values) AS tag_value
        FROM platform_exceptions_agg p
    ), almost_done AS (
     SELECT
        p1.platform,
        ARRAY_AGG(
            NAMED_STRUCT(
            'value', p1.tag_value, 
            'name', cpt.name, 
            'summary', cpt.summary,
            'additional_info', 
                CASE 
                    WHEN 
                        ptfa.product IS NOT NULL 
                    THEN ptfa.support_level_desc
                    ELSE CONCAT(INITCAP(cpt.tag_type), ' is not mapped to any Focus Areas') 
                END
            )
        ) AS tags
        FROM platform_exceptions_exploded p1
        JOIN catalog_product_tags cpt ON p1.tag_value = cpt.tag_value
        LEFT OUTER JOIN ptfa ON p1.platform = ptfa.platform AND ptfa.product = cpt.name 
        GROUP BY 1
    ) SELECT
        ad.platform,
        ad.tags,
        p.products_without_service_tags
      FROM almost_done ad
      JOIN platform_exceptions_agg p ON ad.platform = p.platform
'''
