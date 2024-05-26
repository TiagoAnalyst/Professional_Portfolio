--Overview of the table 

SELECT *
FROM [Meat Production].dbo.[global-food]

--Check if certain columns has only nulls and, in this way, exclude those columns from the table

SELECT count([Product])  AS [Product_Number of nulls]
,count([Yield (t/ha)])  AS [Yield(t/ha_Number of nulls]
,count([Yield (kg/animal)])  AS [Yield_kg_animal_Number of nulls]
,count([Land_Use (ha)])  AS [Land_Use_Number of nulls]
,count([area_harvested__ha__per_capita])  AS [area_per_capita_Number of nulls]
,count([Land Use per capita (mÂ²)])  AS [land_use_per_capita_Number of nulls]
FROM [Meat Production].dbo.[global-food]

--Check the unique values for the column "Country"

SELECT DISTINCT [Country] 
FROM [Meat Production].dbo.[global-food]

--Rename the column name "Country" to "Locations" using the Object Explorer

--"Country" column entries grouped by FAO, countries and continents

ALTER TABLE [Meat Production].dbo.[global-food]
ADD [Locations_group] AS 
(CASE 
	WHEN [Locations] LIKE ('%(FAO)%') THEN 'FAO'
	WHEN [Locations] LIKE ('Europe') THEN 'Continent'
	WHEN [Locations] LIKE ('Africa') THEN 'Continent'
	WHEN [Locations] LIKE ('%Asia%') THEN 'Continent'
	WHEN [Locations] LIKE ('%North America%') THEN 'Continent'
	WHEN [Locations] LIKE ('%South America%') THEN 'Continent'
	WHEN [Locations] LIKE ('%Oceania%') THEN 'Continent'
	WHEN [Locations] LIKE ('%European Union (27)') THEN 'European Union (27)'
	WHEN [Locations] LIKE ('%income countries%') THEN 'Country wealth class'
	WHEN [Locations] LIKE ('%World%') THEN 'World'
	ELSE 'Country'
END)

--Table preview - NEW 
SELECT *
FROM [Meat Production].dbo.[global-food]
WHERE[Locations_group] LIKE 'country'

--Meat production per capita (kg), slaughtered animals per capita, food supply by continent

SELECT [Year]
		,[Locations]
		,[Production per capita (kg)]
		,[Producing or slaughtered animals]
		,[Producing or slaughtered animals]/[Production (t)] AS 'No. Animals killed to produce a ton of meat'
		,[Food supply (g per capita per day)]
FROM [Meat Production].dbo.[global-food]
WHERE [Locations_group] LIKE 'Continent'

 
-- Biggest meat producers by continent 

SELECT TOP 10 [Locations],[Production per capita (kg)],[Production (t)], Year
FROM [Meat Production].dbo.[global-food]
WHERE [Locations_group] LIKE 'Continent'
AND [YEAR] LIKE 2021
ORDER BY [Production per capita (kg)] DESC

--Meat Production per capita (kg)/Meat imports/exports/Domestic supply by country

SELECT [Locations]
		,[Year]
		,Round([Production per capita (kg)],1) as [Production per capita (kg)]
		,[Imports per capita (kg)]
		,[Exports per capita (kg)]
		,[Domestic supply per capita (kg)]
FROM  [Meat Production].dbo.[global-food]
WHERE [Locations_group] LIKE 'Country' 
ORDER BY [Locations] 

--Year with highest number of animals slaughtered by country

SELECT [Year]
		,[Locations]
		,[Production (t)]
		,[Producing or slaughtered animals]/[Production (t)] AS 'No. Animals killed to produce a ton of meat'
		,[Producing or slaughtered animals]
FROM [Meat Production]..[global-food]
WHERE [Locations_group] LIKE 'Country'


--Country with the highest production of meat 

SELECT TOP 1 [Year]
		,[Locations]
		,[Production (t)]
		,[Producing or slaughtered animals]
FROM [Meat Production]..[global-food]
WHERE [Locations_group] LIKE 'Country'
Order by [Production (t)] DESC

--Percentage meat allocation per sector (human food, industrial uses, animal feed)

SELECT [Locations]
	   ,[Year]
	   ,[Food supply (g per capita per day)]
FROM [Meat Production].dbo.[global-food]
WHERE [Locations_group] LIKE 'FAO'


