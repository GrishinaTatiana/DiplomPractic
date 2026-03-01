import matplotlib.pyplot as plt
from scipy.optimize import minimize
import numpy as np
from scipy.integrate import odeint

# установленная общая численность населения
N = 1000
# начальное число инфицированных и выздоровевших, I0 и R0
I0, R0 = 1, 0
# все остальные изначально восприимчивы к инфекции, S0
S0 = N - I0 - R0
# бета-частота контакта и средняя гамма-частота восстановления (за 1 день)
beta, gamma = 0.4, 1./10
# сетка временных точек (в днях)
t = np.linspace(0, 90, 90)  # 90 = 6*15
# данные. Здесь: грипп в британской школе-интернате, 1978 год.
data = [1, 3, 6, 25, 73, 222, 294, 258, 237, 191, 125, 69, 27, 11, 4]

# дифференциальные уравнения модели SIR:
def deriv(y, t, N, beta, gamma):
    S, I, R = y
    dSdt = -beta * S * I / N
    dIdt = beta * S * I / N - gamma * I
    dRdt = gamma * I
    return dSdt, dIdt, dRdt

# вектор начальных условий:
y0 = S0, I0, R0
# интегрирование уравнения SIR по временной сетке t:
ret = odeint(deriv, y0, t, args=(N, beta, gamma))
S, I, R = ret.T

# построение данных на трех отдельных кривых для S(t), I(t) и R(t).:
scale_Factor =1

fig = plt.figure(2, facecolor='w')
plt.clf()
ax = fig.add_subplot(111, axisbelow=True)
ax.plot(t, S/scale_Factor,  alpha=0.5, lw=2, label='Susceptible')
ax.plot(t, I/scale_Factor,  alpha=0.5, lw=2, label='Infected')
ax.plot(t, R/scale_Factor,  alpha=0.5, lw=2, label='Recovered with immunity')
ax.plot(np.arange(0,6*15,6),data,"k*:", label='Original Data')

ax.set_xlabel('Time /days')
ax.set_ylabel('Number (1000s)')
ax.yaxis.set_tick_params(length=0)
ax.xaxis.set_tick_params(length=0)
legend = ax.legend()
legend.get_frame().set_alpha(0.5)
for spine in ('top', 'right', 'bottom', 'left'):
    ax.spines[spine].set_visible(False)
plt.title('SIR Model without fit to the data (initial conditions)')
plt.savefig('Model without fit.png', dpi=200)
plt.show()