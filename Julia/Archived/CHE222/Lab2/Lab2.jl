include("EmpiricalP.jl");
using Plots;
TempArray = collect(300:10:600)
Pressure = EmpiricalPressure(TempArray);
plot(TempArray, Pressure, label="Pressure")
xlabel!("Temperature")
ylabel!("Pressure")
plot!(legend=:outerbottom, show=true)
