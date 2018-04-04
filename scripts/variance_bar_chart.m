fname = 'solartracking_results.json'; 
fid = fopen(fname); 
raw = fread(fid,inf);
str = char(raw'); 
fclose(fid); 
val = jsondecode(str);

axes1 = axes('Parent',figure);
grid on
           
variance = [[val(1).variance, val(2).variance, val(3).variance, val(4).variance],
              [val(1).variance, val(2).variance, val(3).variance, val(4).variance],
              [val(1).variance, val(2).variance, val(3).variance, val(4).variance]]

x=linspace(1, 12, size(variance, 1));
colormap([0,1,0; 0,0,1; 1,0,0; 1,1,0]);   
 
bar3(x, variance,'grouped') 

set(gcf,'color','w');
set(gca,'xcol','black','ycol','black')
set(gca, 'FontName', 'Fira Code')
set(gca, 'GridAlpha', 1.)
 
xlabel('location')
ylabel('month')
zlabel('variance')

set(axes1,'XTick',[1 2 3 4],'XTickLabel',...
     {'jan','feb','mar','apr'});