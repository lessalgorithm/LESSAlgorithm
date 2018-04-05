axes1 = axes('Parent',figure);
grid on

width = 1;
figure(1); 
hold on;

locationDatasets = {'1522955790_TORTotal_solartracking_results.json', 
                    '1522955991_NYCTotal_solartracking_results.json', 
                    '1522955717_HTITotal_solartracking_results.json'}

for location=1:3
    xval=location;    
    
    vector = getPredTimeWastedForLocation(locationDatasets{location});
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
set(gca, 'FontName', 'Fira Code')
set(gca, 'GridAlpha', 1.)

xlabel('location')
ylabel('month')
zlabel('% time wasted')

set(axes1,'YTick',[1 2 3 4],'YTickLabel',...
    {'jan-march','april-june','jul-sep','oct-dec'});

set(axes1,'XTick',[1 2 3 4],'XTickLabel',...
     {'Toronto','New York','Haiti'});

view(axes1,[152.30993247402 60.4]);
 
function perTimeWasted = getPredTimeWastedForLocation(jsonFile)
    fname = jsonFile; 
    fid = fopen(fname); 
    raw = fread(fid,inf);
    str = char(raw'); 
    fclose(fid);
    val = jsondecode(str);
    
    %                       static                 orchas               eno                     less
    perTimeWasted = [[val(1).perTimeWasted, val(5).perTimeWasted, val(9).perTimeWasted, val(13).perTimeWasted],
                     [val(2).perTimeWasted, val(6).perTimeWasted, val(10).perTimeWasted, val(14).perTimeWasted],
                     [val(3).perTimeWasted, val(7).perTimeWasted, val(11).perTimeWasted, val(15).perTimeWasted],
                     [val(4).perTimeWasted, val(8).perTimeWasted, val(12).perTimeWasted, val(16).perTimeWasted]];
end