import zdsim as zds
import starsim as ss
import sciris as sc


def make_zd(sim_pars=None):
    spars = dict(
        unit = 'day', dt = 7, start = sc.date('2013-01-01'), stop = sc.date('2016-12-31'), rand_seed = 123,
    )
    if sim_pars is not None:
        spars.update(sim_pars)

    pop = ss.People(n_agents=1000)
  
    tb = zds.ZD(dict(
        beta = ss.beta(0.1),
        init_prev = ss.bernoulli(p=0.25),
        unit = 'day'
    ))
    sim = ss.Sim(
        people=pop,
        networks=net,
        diseases=zd,
        demographics=[deaths, births],
        pars=spars,
    )

    sim.pars.verbose = sim.pars.dt / 365

    return sim

if __name__ == '__main__':
    sim_zd = make_zd()
    sim_zd.run()
    sim_zd.diseases['zd'].plot()
    plt.show()
