from fuzzylogic.classes import Domain, Rule
from fuzzylogic.functions import S, trapezoid, R


class FuzzyLogic:
    """
    This class implements simple fuzzy logic for drone movements control.
    """

    def __init__(self):
        """
        Define domains of variables, functions for given ranges and rules.
        """

        self.result_distance = Domain("Result Distance", 0, 10000)
        self.distance_diff = Domain("Distance Difference", -100, 100)
        self.result_height = Domain("Result Height", 0, 300)
        self.result_width = Domain("Result Width", 0, 100)

        self.final_speed = Domain("Final Speed", -30, 100)
        self.old_speed = Domain("Old Speed", -30, 100)
        self.height = Domain("Height", -50, 50)
        self.width = Domain("Width", -50, 50)

        self.result_distance.far_behind = S(0, 200)
        self.result_distance.in_place = S(150, 250)
        self.result_distance.close = trapezoid(200, 225, 275, 350)
        self.result_distance.far = trapezoid(300, 500, 600, 650)
        self.result_distance.very_far = R(650, 1000)

        self.distance_diff.no_change = trapezoid(-20, -5, 5, 20)
        self.distance_diff.forward_change = R(10, 100)
        self.distance_diff.backward_change = S(-100, -10)

        self.result_height.in_place = trapezoid(-20, -15, 10, 15, c_m=1)
        self.result_height.up = R(15, 25)
        self.result_height.down = S(-25, -15)

        self.result_width.in_place = trapezoid(-20, -15, 10, 15, c_m=1)
        self.result_width.right = R(15, 25)
        self.result_width.left = S(-25, -15)

        self.final_speed.forward_slow = trapezoid(0, 3, 7, 15)
        self.final_speed.forward_medium = trapezoid(13, 17, 27, 35)
        self.final_speed.forward_fast = R(30, 100)
        self.final_speed.backward_slow = trapezoid(-10, -7, -3, 0)
        self.final_speed.backward_medium = S(-30, -8)
        self.final_speed.idle = trapezoid(-3, -2, 2, 3)

        self.old_speed.forward_slow = trapezoid(0, 3, 7, 15)
        self.old_speed.forward_medium = trapezoid(13, 17, 27, 35)
        self.old_speed.forward_fast = R(30, 100)
        self.old_speed.backward_slow = trapezoid(-10, -7, -3, 0)
        self.old_speed.backward_medium = S(-30, -8)
        self.old_speed.idle = trapezoid(-3, -2, 2, 3)

        self.height.do_not_move = trapezoid(-2, -1, 1, 2, c_m=1)
        self.height.move_up = R(2, 15)
        self.height.move_down = S(-15, 2)

        self.width.do_not_move = trapezoid(-2, -1, 1, 2, c_m=1)
        self.width.rotate_right = R(2, 15)
        self.width.rotate_left = S(-15, 2)

        self.distance_rules = Rule(
            {
                (self.result_distance.in_place, self.result_distance.in_place): self.final_speed.idle,
                (self.result_distance.far_behind, self.result_distance.far_behind): self.final_speed.backward_medium,
                (self.result_distance.close, self.result_distance.close): self.final_speed.forward_slow,
                (self.result_distance.far, self.result_distance.far): self.final_speed.forward_medium,
                (self.result_distance.very_far, self.result_distance.very_far): self.final_speed.forward_fast,
            }
        )

        self.speed_rules = Rule(
            {
                (self.old_speed.idle, self.distance_diff.forward_change): self.final_speed.backward_slow,
                (self.old_speed.idle, self.distance_diff.backward_change): self.final_speed.forward_slow,
                (self.old_speed.backward_slow, self.distance_diff.no_change): self.final_speed.backward_medium,
                (self.old_speed.backward_slow, self.distance_diff.forward_change): self.final_speed.backward_medium,
                (self.old_speed.forward_slow, self.distance_diff.no_change): self.final_speed.forward_medium,
                (self.old_speed.forward_slow, self.distance_diff.backward_change): self.final_speed.forward_fast,
                (self.old_speed.forward_medium, self.distance_diff.backward_change): self.final_speed.forward_fast,
                (self.old_speed.forward_medium, self.distance_diff.no_change): self.final_speed.forward_fast,
            }
        )

        self.height_rules = Rule(
            {
                (self.result_height.in_place, self.result_height.in_place): self.height.do_not_move,
                (self.result_height.up, self.result_height.up): self.height.move_up,
                (self.result_height.down, self.result_height.down): self.height.move_down,
            }
        )

        self.width_rules = Rule(
            {
                (self.result_width.in_place, self.result_width.in_place): self.width.do_not_move,
                (self.result_width.right, self.result_width.right): self.width.rotate_right,
                (self.result_width.left, self.result_width.left): self.width.rotate_left,
            }
        )

    def get_width_prediction(self, width_value: float) -> float:
        """
        Get width (yaw angle) value, that corresponds to drone movement.
        Parameters
        ----------
        width_value - exact value that correspond to drone movement.

        Returns
        -------
        Value of width (yaw angle) that correspond to drone movement.
        It should be less than exact value, because we want the drone to move gradually.
        """
        width_dict = {self.result_width: width_value, self.result_width: width_value}
        return self.width_rules(width_dict)

    def get_height_prediction(self, height_value: float) -> float:
        """
        Get height value, that corresponds to drone movement.
        Parameters
        ----------
        height_value - exact value that correspond to drone movement.

        Returns
        -------
        Value of height that correspond to drone movement.
        It should be less than exact value, because we want the drone to move gradually.
        """
        height_dict = {self.result_height: height_value, self.result_height: height_value}
        return self.height_rules(height_dict)

    def get_speed_prediction(self, distance_value: float, distance_diff: float, old_speed: float) -> float:
        """
        Get speed of the drone calculated by fuzzy logic using speed and distance rules.
        Parameters
        ----------
        distance_value - distance between drone and detected object.
        distance_diff - difference between current and previous distance to detected object.
        old_speed - previously returned speed

        Returns
        -------
        Value of drone speed.
        """
        distance_dict = {self.result_distance: distance_value, self.result_distance: distance_value}
        speed_dict = {self.old_speed: old_speed, self.distance_diff: distance_diff}
        distance_result = self.distance_rules(distance_dict)
        speed_result = self.speed_rules(speed_dict)
        if speed_result is None:
            result = distance_result
        elif distance_result is None:
            result = speed_result
        else:
            result = 0.8 * distance_result + 0.2 * speed_result
        return result
