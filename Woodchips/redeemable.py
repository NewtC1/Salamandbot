from Woodchips_StreamlabsSystem import change_points


class Redeemable():

    def __init__(self, name, description, cost, user, user_input=None, args=None):
        """

        :param name: Name of the redeemable
        :param description: What the user will see when it's redeemed.
        :param cost: The cost in woodchips.
        :param user: The user's name.
        """
        self.name = name
        self.description = description
        self.cost = cost
        self.user = user
        self.custom_function = user_input
        self.args = args

    def redeem(self):
        if change_points(self.user, self.cost):
            if self.custom_function:
                if self.args:
                    self.custom_function(self.args)
                else:
                    self.custom_function()

            return True
        else:
            return False
