import starsim as ss
import sciris as sc
import zdsim as zds
import numpy as np
class ZeroDoseVaccination(ss.Intervention):
    """
    Base class for any intervention that uses campaign delivery; handles interpolation of input years.
    """

    def __init__(self,  year=[1900], 
                 rate =.015, 
                 target_gender='All', 
                 target_age=5, 
                 target_state=zds.TST.NONE, 
                 new_value_fraction=1, 
                 prob=None, 
                 *args, **kwargs):
        
        self.int_year = year
        self.rate = sc.promotetoarray(rate)
        self.target_gender = target_gender
        self.target_age = target_age
        self.prob = sc.promotetoarray(prob)
        self.target_state = target_state
        self.new_value_fraction = new_value_fraction
        super().__init__(*args, **kwargs)
        return

    def init_pre(self, sim):
        super().init_pre(sim)
        return
    
    def step(self):  #update(self, sim):
        sim = self.sim
        
        if self.sim.t.now('year') >= 1000:
            print("intervention year reached")
            

        tetanus = sim.diseases['tetanus']
        ppl = sim.people
        
        # eligible = (tetanus.state == self.target_state) & ppl.alive & (ppl.age >= self.target_age) & (ppl.gender == self.target_gender)
        eligible = (tetanus.state == self.target_state) & ppl.alive
        
        eligible_uids = eligible.uids
        change_uids = eligible_uids[np.random.rand(len(eligible_uids)) < self.rate]
        # TODO: Add the actual value of the product's effectiveness here...
        tetanus.minerva_column[change_uids] = tetanus.minerva_column[change_uids]+0.1 # *self.product.efficacy   
        
        return len(change_uids)
