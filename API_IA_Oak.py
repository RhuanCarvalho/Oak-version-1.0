
from io import BytesIO
import json
from flask import Flask, request
import pandas as pd
from Classes.DecisionApi import BetterWinner



if __name__ =='__main__':

    app = Flask(__name__)
    IA = BetterWinner()


    @app.route('/apiOak', methods=["POST"])
    def apiOak():

        df = json.load((BytesIO(request.get_data())))

        candles = pd.json_normalize(df)

        response = IA.decision_the_better(candles)

        return {"Buy(1)/Sell(-1)" : response }


    app.run(debug=True)

