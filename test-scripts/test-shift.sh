#!/bin/bash
set -e

: ${MEAL_PLANNER_API_TOKEN:?must set \$MEAL_PLANNER_API_TOKEN}

DATE="2022-03-14"
SHIFT_MODE="all"

# wait-for-it.sh 127.0.0.1:8000 --timeout 60

echo -e "\nClearing database"
http delete :8000/meals/week/10 x-token:$MEAL_PLANNER_API_TOKEN -ph | head -1
http delete :8000/meals/week/11 x-token:$MEAL_PLANNER_API_TOKEN -ph | head -1
http delete :8000/meals/week/12 x-token:$MEAL_PLANNER_API_TOKEN -ph | head -1

echo -e "\nPutting dummy data in database"
http post :8000/meals/bulk x-token:$MEAL_PLANNER_API_TOKEN < test-scripts/test-data.json > /dev/null
http :8000/meals x-token:$MEAL_PLANNER_API_TOKEN -pb | jtbl

echo -e "\nExecuting shift ($DATE, $SHIFT_MODE)"
http put :8000/meals/shift/$DATE x-token:$MEAL_PLANNER_API_TOKEN mode==$SHIFT_MODE -pb | jtbl
echo ""
http :8000/meals x-token:$MEAL_PLANNER_API_TOKEN -pb | jtbl
