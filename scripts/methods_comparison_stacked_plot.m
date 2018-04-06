fname = '1523026460_7_days_NYCTotal_solartracking_results.json';
fid = fopen(fname);
raw = fread(fid,inf);
str = char(raw');
fclose(fid);
val = jsondecode(str);

axes1 = axes('Parent',figure);
hold all
grid on
colors = {1/255*[0, 179, 179], 1/255*[51, 153, 255], 1/255*[249, 188, 6]}
% 1/255*[204, 102, 0]
h = {};

set(gcf,'color','w');
set(gca,'xcol','black','ycol','black')
set(gca, 'FontName', 'Fira Code')
set(gca, 'GridAlpha', 1.)

xlabel('timeslot (t)')
ylabel('method')
zlabel('duty cycle (D_t)')

set(axes1,'YTick',[1 2 3],'YTickLabel',...
    {'static','ENO-baseline','LESS'});

for j = 1:3
    [rows_duty_cycle,cols_duty_cycle] = size(val(j).sense_freq);
    [rows_taget_req,cols_target_req] = size(val(j).orchas);   
    slot_matrix = 0:1:rows_duty_cycle-1;

    h{end+1} = plot3(slot_matrix, j*ones(size(slot_matrix)), val(j*4).sense_freq, 'color', colors{j}, 'LineWidth', 3.5);
    h{end+1} = plot3(slot_matrix, j*ones(size(slot_matrix)), val(j*4).orchas, 'LineStyle', ':', 'color', 'red', 'LineWidth', 2.5);      
end

legend([h{1} h{3} h{5} h{6}],{'static', 'ENO-Kansal', 'LESS', 'target'});

view(axes1,[-134.09006752598 66.1729713465918]);