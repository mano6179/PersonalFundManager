from fastapi import APIRouter, UploadFile, File
from fastapi.responses import JSONResponse
import pandas as pd
from typing import List, Dict
import io

router = APIRouter()

@router.post("/upload-excel")
async def upload_excel(file: UploadFile = File(...)):
    try:
        # Read the Excel file
        contents = await file.read()
        excel_file = io.BytesIO(contents)
        
        # Get all sheet names
        xls = pd.ExcelFile(excel_file)
        sheet_names = xls.sheet_names
        
        # Read each sheet and get its structure
        sheets_data = {}
        for sheet_name in sheet_names:
            df = pd.read_excel(excel_file, sheet_name=sheet_name)
            sheets_data[sheet_name] = {
                "columns": df.columns.tolist(),
                "row_count": len(df),
                "sample_data": df.head(5).to_dict(orient='records')
            }
        
        return JSONResponse(content={
            "message": "File processed successfully",
            "sheets": sheets_data
        })
    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"message": f"Error processing file: {str(e)}"}
        ) 