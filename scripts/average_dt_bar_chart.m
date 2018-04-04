fname = 'solartracking_results.json'; 
fid = fopen(fname); 
raw = fread(fid,inf);
str = char(raw'); 
fclose(fid); 
val = jsondecode(str);

axes1 = axes('Parent',figure);
grid on
           
average_dt = [[val(1).Dt_average, val(2).Dt_average, val(3).Dt_average, val(4).Dt_average],
              [val(1).Dt_average, val(2).Dt_average, val(3).Dt_average, val(4).Dt_average],
              [val(1).Dt_average, val(2).Dt_average, val(3).Dt_average, val(4).Dt_average] ]

x=linspace(1, 12, size(average_dt, 1));
colormap([0,1,0; 0,0,1; 1,0,0; 1,1,0]);   
 
bar3(x, average_dt,'grouped') 

set(gcf,'color','w');
set(gca,'xcol','black','ycol','black')
set(gca, 'FontName', 'Fira Code')
set(gca, 'GridAlpha', 1.)
 
xlabel('location')
ylabel('month')
zlabel('average duty cycle (D_t)')

set(axes1,'XTick',[1 2 3 4],'XTickLabel',...
     {'jan','feb','mar','apr'});