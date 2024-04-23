import asyncio
import copy
import datetime
import json
from typing import Any, Dict, List, Tuple

from tinkoff.invest import CandleInterval

from strategies.prediction import Prediction
from strategies.settings_strategies import broker_commission, learning_time


class Te:
    @staticmethod
    def _run_share(
        analyze_share_data: Dict[str, Any], check_data_share: Dict[str, Any], total_sum: float, path_file: str
    ) -> Dict[str, Any] | None:
        with open(f"LOG_{path_file}.log", "w") as f:
            json.dump("", f)
        begin_sum = total_sum
        history = Te._translate_date(analyze_share_data["history"]["history"][1:])
        check_history = Te._translate_date(check_data_share["history"]["history"][1:])

        if len(history) < learning_time:
            return None

        test_data = copy.deepcopy(analyze_share_data)
        test_data["history"] = history[:learning_time]
        recommendation = Prediction.get_trend_predict(test_data)
        flag_recommendation = True
        if recommendation:
            flag_recommendation = False

        # stop = 0
        take_profit = 0
        trade_open = False
        open_price = 0
        close_prices = 0
        count_shares = 0
        count_close = 0
        count_profit = 0
        i = learning_time - 1
        while i <= len(history) - 2:
            i += 1
            # for i in range(learning_time, len(history)):
            if not (trade_open):
                if flag_recommendation:
                    test_data["history"] = history[: i + 1]
                    recommendation = Prediction.get_trend_predict(test_data)
                    if recommendation:
                        close_prices = recommendation["close"]
                        take_profit = recommendation["take profit"]
                        open_price = recommendation["open"]
                        flag_recommendation = True
                        with open(f"write_data_test\\TEST_{path_file}\\{test_data["ticker"]}.json", "w") as f:
                            recommendation_str = (
                                f"Рекомендация:\n"
                                f"open: {open_price}\n"
                                f"close: {close_prices}\n"
                                f"take_profit: {take_profit}\n"
                                f"time: {str(history[i][0])}\n\n"
                            )
                            f.write(recommendation_str)
                            # print(recommendation_str)
                    else:
                        continue

                if history[i][2] <= open_price:
                    trade_open = True
                    open_price = history[i][2]
                    base_prices = history[i][2] * (1 + broker_commission) * analyze_share_data["lot"]
                    count_shares = total_sum // base_prices
                    total_sum -= count_shares * base_prices
                    with open(f"LOG_{path_file}.log", "a") as f:
                        close_str = (
                            f"Сделка открыта:\n"
                            f"open: {open_price}\n"
                            f"count_shares: {count_shares}\n"
                            f"total_sum: {total_sum}\n"
                            f"time: {str(history[i][0])}\n\n"
                        )
                        f.write(close_str)
                        # print(close_str)

            elif trade_open:
                close_order = Te._check_recomendation(
                    date_from=history[i][0], check_data_share=check_history, close=close_prices, take=take_profit
                )
                if close_order["status"] == "close":
                    close_prices = close_order["close"]
                    time = close_order["time"]
                    for j in range(i, len(history)):
                        if history[j][0] <= time:
                            i = j
                            break
                    count_close += 1
                    base_prices = close_prices * (1 - broker_commission) * analyze_share_data["lot"]
                    total_sum += base_prices * count_shares
                    trade_open = False
                    flag_recommendation = False

                    with open(f"LOG_{path_file}.log", "a") as f:
                        close_str = (
                            f"Сделка закрыта по стопу:\n"
                            f"close: {base_prices}\n"
                            f"count_shares: {count_shares}\n"
                            f"total_sum: {total_sum}\n"
                            f"time: {str(time)}\n"
                            f"-------------------------------------------------\n"
                        )
                        f.write(close_str)
                        # print(close_str)
                elif close_order["status"] == "take":
                    close_prices = close_order["take"]
                    time = close_order["time"]
                    for j in range(i, len(history)):
                        if history[j][0] <= time:
                            i = j
                            break
                    count_profit += 1
                    base_prices = close_prices * (1 - broker_commission) * analyze_share_data["lot"]
                    total_sum += base_prices * count_shares
                    trade_open = False
                    flag_recommendation = False
                    with open(f"LOG_{path_file}.log", "a") as f:
                        close_str = (
                            f"Сделка закрыта по тейку:\n"
                            f"close: {close_prices}\n"
                            f"count_shares: {count_shares}\n"
                            f"total_sum: {total_sum}\n"
                            f"time: {str(time)}\n"
                            f"-------------------------------------------------\n"
                        )
                        f.write(close_str)
                        # print(close_str)
                elif close_order["status"] == "end":
                    time = close_order["time"]
                    close_prices = close_order["close_price"]
                    base_prices = close_prices * (1 - broker_commission) * analyze_share_data["lot"]
                    total_sum += base_prices * count_shares
                    trade_open = False
                    flag_recommendation = False
                    with open(f"LOG_{path_file}.log", "a") as f:
                        close_str = (
                            f"Сделка закрыта:\n"
                            f"close: {close_prices}\n"
                            f"count_shares: {count_shares}\n"
                            f"total_sum: {total_sum}\n"
                            f"time: {str(time)}\n"
                            f"-------------------------------------------------\n"
                        )
                        f.write(close_str)
                        # print(close_str)

        result = {}
        result["ticker"] = analyze_share_data["ticker"]
        result["count_order"] = count_profit + count_close
        result["count_take"] = count_profit
        result["count_close"] = count_close
        result["total_sum"] = total_sum
        result["total_result"] = total_sum - begin_sum
        result["relative_sum"] = str((total_sum - begin_sum) / total_sum * 100) + "%"
        return result

    @staticmethod
    def _check_recomendation(
        date_from: Any, check_data_share: List[List[Any]], close: float, take: float
    ) -> Dict[str, Any]:
        index_from = 0
        for i in range(len(check_data_share)):
            if date_from <= check_data_share[i][0]:
                index_from = i
                break

        check_data_share = check_data_share[index_from - 1 :]

        for i in range(len(check_data_share)):
            if check_data_share[i][4] <= close:
                result = {"status": "close"}
                result["close"] = check_data_share[i][4]
                result["time"] = check_data_share[i][0]
                return result
            elif check_data_share[i][2] >= take:
                result = {"status": "take"}
                result["take"] = check_data_share[i][2]
                result["time"] = check_data_share[i][0]
                return result

        result = {"status": "end"}
        result["close_price"] = check_data_share[-1][2]
        result["time"] = check_data_share[-1][0]
        return result

    @staticmethod
    def _translate_date(history: List[List[str]]) -> List[List[datetime]]:  # type: ignore
        from datetime import datetime

        # Преобразование каждого элемента списка в формат datetime
        for i in range(len(history)):
            date_str = history[i][0]
            date_dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S%z")
            history[i][0] = date_dt  # type: ignore
        return history

    @staticmethod
    async def run_interval_time(path: str) -> Tuple[float, str]:
        from statistics import mean

        with open(path + ".json") as f:  # noqa
            list_shares = json.load(f)
        with open("CANDLE_INTERVAL_5_MIN.json") as f:  # noqa
            list_check_data_share = json.load(f)

        total_sum = 100000
        result_check = []
        array_total_sum = []
        for i in range(len(list_shares)):
            result = Te._run_share(list_shares[i], list_check_data_share[i], total_sum, path)
            if result:
                result_check.append(result)
                array_total_sum.append(result["total_sum"])

        average_sum = mean(array_total_sum)
        average_procent = str((average_sum - total_sum) / total_sum * 100) + "%"
        result_check.append({"average_sum": average_sum, "average_procent": average_procent})
        with open(f"Test_{path}.json", "w") as f:  # noqa
            json.dump(result_check, f)

        print(f"{path}\nSum: {average_sum}\nProcent: {average_procent}\n---------------------------------------------")

        return (average_sum, average_procent)


if __name__ == "__main__":
    list_timeframe = [
        CandleInterval.CANDLE_INTERVAL_DAY,
        CandleInterval.CANDLE_INTERVAL_4_HOUR,
        CandleInterval.CANDLE_INTERVAL_HOUR,
        CandleInterval.CANDLE_INTERVAL_30_MIN,
        CandleInterval.CANDLE_INTERVAL_15_MIN,
        CandleInterval.CANDLE_INTERVAL_5_MIN,
    ]
    result_test = []

    for i in range(len(list_timeframe)):
        [average_sum, average_procent] = asyncio.run(Te.run_interval_time(str(list_timeframe[i].name)))
        result_test.append({"average_sum": average_sum, "average_procent": average_procent})
    with open("Test_result.json", "w") as f:
        json.dump(result_test, f)
