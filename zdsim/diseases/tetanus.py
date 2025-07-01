import starsim as ss

__all__ = ['Tetanus']


class Tetanus(ss.Infection):
    """
    Tetanus infection model focused on children under age 5.

    Tetanus is modeled as non-contagious: infection occurs from environmental exposure,
    with per-timestep risk applied only to susceptible children under 5.
    """
    def __init__(self, pars=None, **kwargs):
        super().__init__()

        self.define_pars(
            beta = 1.0,  # Not used in this model as tetanus is non-contagious
            exposure_risk = ss.bernoulli(p=0.001),  # Daily risk of exposure for <5yo
            dur_inf = ss.normal(loc=ss.days(10)),   # Duration of illness (days)
            p_death = ss.bernoulli(p=0.2),          # Mortality rate
        )
        self.update_pars(pars=pars, **kwargs)


        # Table to store agent information -
        self.define_states(
            ss.State('susceptible', default=True, label='Susceptible'),
            ss.State('infected', label='Infected'),
            ss.State('recovered', label='Recovered'),
            ss.FloatArr('ti_infected', label='Time of infection'),
            ss.FloatArr('ti_recovered', label='Time of recovery'),
            ss.FloatArr('ti_dead', label='Time of death'),
        )
        return

    def step(self):
        super().step()
        sim = self.sim

        # Identify susceptible children under age 5
        under5 = sim.people.age < 5
        sus_under5 = self.susceptible & under5

        # Apply environmental exposure risk
        exposed = self.pars.exposure_risk.rvs(sus_under5)
        new_infections = sus_under5.uids[exposed]
        if len(new_infections):
            self.set_prognoses(new_infections)
        return

    def set_prognoses(self, uids, sources=None):
        super().set_prognoses(uids, sources)
        ti = self.ti
        p = self.pars

        self.susceptible[uids] = False
        self.infected[uids] = True
        self.ti_infected[uids] = ti

        dur_inf = p.dur_inf.rvs(uids)
        will_die = p.p_death.rvs(uids)

        dead_uids = uids[will_die]
        rec_uids = uids[~will_die]

        self.ti_dead[dead_uids] = ti + dur_inf[will_die]
        self.ti_recovered[rec_uids] = ti + dur_inf[~will_die]
        return

    def step_state(self):
        ti = self.ti

        # Progress infected to recovered
        recovered = (self.infected & (self.ti_recovered <= ti)).uids
        self.infected[recovered] = False
        self.recovered[recovered] = True

        # Trigger deaths
        dead = (self.ti_dead <= ti).uids
        if len(dead):
            self.sim.people.request_death(dead)
        return

    def step_die(self, uids):
        for state in ['susceptible', 'infected', 'recovered']:
            self.statesdict[state][uids] = False
        return


if __name__ == '__main__':
    dis = Tetanus()
    # routine = ss.routine_vx(name='penta', prob=0.6, start_year=2023, age_range=[5], product='pentadose')
    sim = ss.Sim(
        n_agents=10000,
        diseases=dis,
        start=2000,
        stop=2026,
        verbose=.25
    )
    sim.run()
    sim.plot()