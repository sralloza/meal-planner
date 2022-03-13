#!/bin/bash
set -e
source /home/sralloza/Documents/meal-planner/.venv/bin/activate
# wait-for-it.sh 127.0.0.1:8000 --timeout 60

echo -e "\nClearing database"
http delete :8000/meals/week/11 x-token:$MEAL_PLANNER_API_TOKEN -ph | head -1

echo -e "\nPutting dummy data in database"
http post :8000/meals/bulk x-token:$MEAL_PLANNER_API_TOKEN < test-scripts/test-data.json > /dev/null
http :8000/meals x-token:$MEAL_PLANNER_API_TOKEN -pb | jtbl

echo -e "\nExecuting shift"
http put :8000/meals/shift/2122-02-08 x-token:$MEAL_PLANNER_API_TOKEN mode==all -pb | jtbl
echo ""
http :8000/meals x-token:$MEAL_PLANNER_API_TOKEN -pb | jtbl
