import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, inspect

async def list_tables():
    # Open the async database connection
    engine = open_async_database_sqlite("testfile.sqlite")
    
    # Create a session
    async with AsyncSession(engine) as session:
        # Use the inspector to get table names
        inspector = inspect(engine)
        table_names = inspector.get_table_names()
        print("Tables in the database:", table_names)
        
    # Close the engine
    await engine.dispose()

# Run the async function
asyncio.run(list_tables())