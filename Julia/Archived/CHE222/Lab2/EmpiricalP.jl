function EmpiricalPressure(Temperature)
    p = Real[];
    
    for i = 1:length(Temperature)
        if Temperature[i] <= 300
            push!(p, NaN);
        elseif Temperature[i] <= 430.07
            push!(p, exp(1.7599 - (323.96/Temperature[i])));
        elseif Temperature[i] <= 515.7
            push!(p, exp(16.25 - (6479.6/Temperature[i]))); 
        elseif Temperature[i] <= 565.48
            push!(p, exp(9.0023 - (2794.9/Temperature[i])));
        else
            push!(p, exp(6.2047 - (1042.4/Temperature[i])));
        end
    end
    
    return p;
end