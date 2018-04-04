fname = 'solartracking_results.json'; 
fid = fopen(fname); 
raw = fread(fid,inf);
str = char(raw'); 
fclose(fid); 
val = jsondecode(str);

axes1 = axes('Parent',figure);
grid on
           
perTimeDead = [[val(1).perTimeDead, val(2).perTimeDead, val(3).perTimeDead, val(4).perTimeDead],
              [val(1).perTimeDead, val(2).perTimeDead, val(3).perTimeDead, val(4).perTimeDead],
              [val(1).perTimeDead, val(2).perTimeDead, val(3).perTimeDead, val(4).perTimeDead] ]

x=linspace(1, 12, size(perTimeDead, 1));
colormap([0,1,0; 0,0,1; 1,0,0; 1,1,0]);   
 
bar3(x, perTimeDead,'grouped') 

set(gcf,'color','w');
set(gca,'xcol','black','ycol','black')
set(gca, 'FontName', 'Fira Code')
set(gca, 'GridAlpha', 1.)
 
xlabel('location')
ylabel('month')
zlabel('% time dead')

set(axes1,'XTick',[1 2 3 4],'XTickLabel',...
     {'jan','feb','mar','apr'});