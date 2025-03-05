import starsim as ss
import sciris as sc
import zdsim as zds

# class OldVaccineProduct(ss.Product):
#     """
#     A class representing a vaccine product.
    
#     This class models vaccine administration and the immune response.
#     """

#     def __init__(self, name, efficacy=0.85, duration=5, **kwargs):
#         """
#         Args:
#             name (str): Name of the vaccine.
#             efficacy (float): Probability of successful immunization.
#             duration (float): Duration of protection in years.
#         """
#         super().__init__(name=name, **kwargs)
#         self.efficacy = efficacy
#         self.duration = duration

#     def administer(self, people, uids):
#         """
#         Administer the vaccine to the given agents and update immunization status.

#         Args:
#             people (ss.People): The population object.
#             uids (array-like): UIDs of individuals receiving the vaccine.
#         """
#         if not len(uids):
#             return
        
#         # Generate a random response to simulate efficacy
#         immune_response = ss.rand(len(uids)) < self.efficacy
        
#         # Update immunization status
#         people.immunized[uids] = immune_response
#         people.immunity_duration[uids] = self.duration  # Store duration of immunity

#         return immune_response

class VaccineProduct(ss.Product):
# class VaccineProduct(ss.Product):    
    """
    Class to define a vaccine product with specific attributes.
    """
    def __init__(self, name, efficacy, duration, doses, **kwargs):
        self.name = name
        self.efficacy = efficacy
        self.doses = doses
        self.duration = duration
        
    def init_pre(self, sim):
        if not self.initialized:
            super().init_pre(sim)
        else:
            return
    def __repr__(self):
        return f"Product(name={self.name}, efficacy={self.efficacy}, doses={self.doses})"
    
    def administer(self, people, inds):
        """ Adminster a Product - implemented by derived classes """
        print("vaccine administered to people")
        
        return

class ZeroDoseVaccination(ss.Intervention):
    """
    Base class for any intervention that uses campaign delivery; handles interpolation of input years.
    """

    def __init__(self, year=[1900], product=None, rate =.015, target_gender='All', target_age=5, 
                 target_state=zds.TetanusStates.NONE, new_value_fraction=1, 
                 prob=None, *args, **kwargs):
        # if product is None:
        #     raise NotImplementedError('No product specified')
        self.year = sc.promotetoarray(year)
        self.rate = sc.promotetoarray(rate)
        self.target_gender = target_gender
        self.target_age = target_age
        self.prob = sc.promotetoarray(prob)
        self.product = product
        self.target_state = target_state
        self.new_value_fraction = new_value_fraction
        
        self.p = ss.bernoulli(p=lambda self, sim, uids: np.interp(sim.year, self.year, self.rate*sim.dt))
        return

    def init_pre(self, sim):
        super().init_pre(sim)
        return
    
    def step(self):  #update(self, sim):
        sim = self.sim
        if sim.ti < self.year[0]:
            return
        if self.product is None:
            raise NotImplementedError('No product specified')

        tetanus = sim.diseases['tetanus']
        ppl = sim.people
        
        # eligible = (tetanus.state == self.target_state) & ppl.alive & (ppl.age >= self.target_age) & (ppl.gender == self.target_gender)
        eligible = (tetanus.state == self.target_state) & ppl.alive
        
        eligible_uids = eligible.uids
        
        change_uids = self.p.filter(eligible_uids)
        
        # TODO: Add the actual value of the product's effectiveness here...
        tetanus.rel_LS_prog[change_uids] = tetanus.rel_LS_prog[change_uids]*0.9 # *self.product.efficacy   
        tetanus.rel_LF_prog[change_uids] = tetanus.rel_LF_prog[change_uids]*0.9  # *self.product.efficacy   
        
        return len(change_uids)

class OldZeroDoseVaccination(ss.Intervention):
    """
    An intervention to implement the Zero Dose Vaccination campaign.

    - Checks if the agent is alive.
    - If alive, checks if the agent is under 5 years old.
    - If under 5, checks immunization status.
    - If not immunized, administers a Zero Dose.
    - If already immunized, checks DPT sequence and administers accordingly.
    """

    def __init__(self, product_zero_dose=None, product_dpt=None, **kwargs):
        """
        Args:
            product_zero_dose (VaccineProduct): The vaccine used for Zero Dose.
            product_dpt (VaccineProduct): The DPT vaccine used for routine doses.
        """
        super().__init__(**kwargs)
        self.product_zero_dose = product_zero_dose
        self.product_dpt = product_dpt
        self.zero_dose_uids = ss.BoolArr('zero_dose')
        self.dpt_doses = ss.FloatArr('dpt_doses', default=0)  # Track DPT doses
        return

    def check_eligibility(self):
        """ Determine eligibility based on age and immunization status. """
        sim = self.sim
        alive_uids = sim.people.alive  # Check if agent is alive
        under_five_uids = sim.people.age[alive_uids] < 5  # Check if agent is under 5
        immunized_uids = ss.uids(sim.people.tetanus.state!= zds.TetanusStates.IMMUNIZED )  # Check if agent is immunized
        
        # zero_dose_uids will be those that are not immunized, under five and alive:
        zero_dose_uids = alive_uids & under_five_uids & immunized_uids
        return zero_dose_uids, immunized_uids

    def step(self):
        """ Apply the Zero Dose Vaccination intervention with DPT sequence. """
        sim = self.sim
        zero_dose_uids, immunized_uids = self.check_eligibility()

        # Administer Zero Dose to non-immunized under-five children
        if len(zero_dose_uids):
            self.sim.interventions.vaccination.zerodosevaccination(zero_dose_uids)
            # self.product_zero_dose.administer(sim.people, zero_dose_uids)
            self.zero_dose_uids[zero_dose_uids] = True  # Mark as zero dose recipients

        # Get current DPT dose counts for immunized children
        current_dpt_doses = self.dpt_doses[immunized_uids]

        # Identify which immunized agents need which DPT dose
        dpt1_uids = immunized_uids[current_dpt_doses == 0]
        dpt2_uids = immunized_uids[current_dpt_doses == 1]
        dpt3_uids = immunized_uids[current_dpt_doses == 2]

        # Administer DPT vaccines
        if len(dpt1_uids):
            self.product_dpt.administer(sim.people, dpt1_uids)
            self.dpt_doses[dpt1_uids] = 1  # Mark as received DPT1

        if len(dpt2_uids):
            self.product_dpt.administer(sim.people, dpt2_uids)
            self.dpt_doses[dpt2_uids] = 2  # Mark as received DPT2

        if len(dpt3_uids):
            self.product_dpt.administer(sim.people, dpt3_uids)
            self.dpt_doses[dpt3_uids] = 3  # Mark as received DPT3

        return zero_dose_uids, immunized_uids


# Example Usage:
if __name__ == "__main__":
    # Create vaccine products
    zero_dose_vaccine = VaccineProduct(name="Zero Dose Vaccine", efficacy=0.75, duration=3, doses=1)
    dpt_vaccine = VaccineProduct(name="DPT Vaccine", efficacy=0.9, duration=5, doses=1)

    # Initialize intervention
    zero_dose_intervention = ZeroDoseVaccination(
        product_zero_dose=zero_dose_vaccine,
        product_dpt=dpt_vaccine
    )

    print(zero_dose_intervention)