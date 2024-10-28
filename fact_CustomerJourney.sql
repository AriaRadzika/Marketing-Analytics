SELECT * FROM dbo.customer_journey
;WITH DuplicateRecords AS (
    SELECT 
        JourneyID,  
        CustomerID, 
        ProductID, 
        VisitDate, 
        Stage, 
        Action, 
        Duration, 
        ROW_NUMBER() OVER (
            PARTITION BY CustomerID, ProductID, VisitDate, Stage, Action  
            ORDER BY JourneyID  
        ) AS row_num 
    FROM 
        dbo.customer_journey  
)

-- Select from the CTE to get records
SELECT *
FROM DuplicateRecords
WHERE row_num = 1
ORDER BY JourneyID;

-- Second query to adjust the duration using COALESCE
;WITH AdjustedRecords AS (
    SELECT 
        JourneyID, 
        CustomerID, 
        ProductID, 
        VisitDate, 
        UPPER(Stage) AS Stage, 
        Action, 
        Duration, 
        AVG(Duration) OVER (PARTITION BY Stage) AS avg_duration, 
        ROW_NUMBER() OVER (
            PARTITION BY CustomerID, ProductID, VisitDate, UPPER(Stage), Action 
            ORDER BY JourneyID 
        ) AS row_num 
    FROM 
        dbo.customer_journey 
)

SELECT 
    JourneyID,  
    CustomerID,  
    ProductID,  
    VisitDate,  
    Stage, 
    Action, 
    COALESCE(Duration, avg_duration) AS Duration 
FROM 
    AdjustedRecords
WHERE 
    row_num = 1;
