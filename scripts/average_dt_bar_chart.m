axes1 = axes('Parent',figure);
grid on

width = 1;
figure(1); 
hold on;

locationDatasets = {'1523020773_TORTotal_solartracking_results.json', 
                    '1523020846_NYCTotal_solartracking_results.json', 
                    '1523020801_HTITotal_solartracking_results.json'}

for location=1:3
    xval=location;    
    
    vector = getPredDt_averageForLocation(locationDatasets{location});
    x=linspace(1, 4, size(vector, 1));
    
    h = bar3(x, vector, width, 'grouped')
    Xdat = get(h,'Xdata');
    for ii=1:length(Xdat)
        Xdat{ii}=Xdat{ii}+(xval-1)*ones(size(Xdat{ii}));
        set(h(ii),'XData',Xdat{ii});
    end    
    
    set(h(1),'facecolor',1/255*[0, 179, 179]);
    set(h(2),'facecolor',1/255*[204, 102, 0]);
    set(h(3),'facecolor',1/255*[51, 153, 255]);
    set(h(4),'facecolor',1/255*[249, 188, 6]);     
end
                
% xlim([0 3]);
view(3);

set(gcf,'color','w');
set(gca,'xcol','black','ycol','black')
set(gca,'FontName', 'Fira Code')
set(gca,'GridAlpha', 1.)

xlabel('location')
ylabel('month')
zlabel('average duty cycle (D_t)')

set(axes1,'YTick',[1 2 3 4],'YTickLabel',...
    {'jan-march','april-june','jul-sep','oct-dec'});

set(axes1,'XTick',[1 2 3 4],'XTickLabel',...
     {'Toronto','New York','Haiti'});
 
function Dt_average = getPredDt_averageForLocation(jsonFile)
    fname = jsonFile; 
    fid = fopen(fname); 
    raw = fread(fid,inf);
    str = char(raw'); 
    fclose(fid);
    val = jsondecode(str);
    
    %                   static             orchas               eno                less
    Dt_average = [[val(1).Dt_average, val(5).Dt_average, val(9).Dt_average, val(13).Dt_average],
                  [val(2).Dt_average, val(6).Dt_average, val(10).Dt_average, val(14).Dt_average],
                  [val(3).Dt_average, val(7).Dt_average, val(11).Dt_average, val(15).Dt_average],
                  [val(4).Dt_average, val(8).Dt_average, val(12).Dt_average, val(16).Dt_average]];
end