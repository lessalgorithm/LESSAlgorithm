axes1 = axes('Parent',figure);
grid on
           
width = 1;
figure(1); 
hold on;

locationDatasets = {'1523010675_TORTotal_solartracking_results.json', 
                    '1522956942_NYCTotal_solartracking_results.json', 
                    '1522956862_HTITotal_solartracking_results.json'}

for location=1:3
    xval=location;    
    
    vector = getPredTimeDeadForLocation(locationDatasets{location});
    x=linspace(1, 3, size(vector, 1));
%     x=linspace(1, 4, size(vector, 1));
    
    h = bar3(x, vector, width, 'grouped') 
    Xdat = get(h,'Xdata');
    for ii=1:length(Xdat)
        Xdat{ii}=Xdat{ii}+(xval-1)*ones(size(Xdat{ii}));
        set(h(ii),'XData',Xdat{ii});
    end    
    
    set(h(1),'facecolor',1/255*[0, 179, 179]);
    set(h(2),'facecolor',1/255*[51, 153, 255]);
%     set(h(2),'facecolor',1/255*[204, 102, 0]);
%     set(h(3),'facecolor',1/255*[51, 153, 255]);
%     set(h(4),'facecolor',1/255*[249, 188, 6]);
    set(h(3),'facecolor',1/255*[249, 188, 6]);
    
    if(location == 3)
%         legend([h(1) h(2) h(3) h(4)],{'static', 'orchestrator', 'ENO baseline', 'LESS', 'target'});
        legend([h(1) h(2) h(3) ],{'static', 'ENO baseline', 'LESS'});
    end    
end

% xlim([0 3]);
view(3);

set(gcf,'color','w');
set(gca,'xcol','black','ycol','black')
set(gca, 'FontName', 'Fira Code')
set(gca, 'GridAlpha', 1.)

xlabel('location')
ylabel('month')
zlabel('% time dead')

set(axes1,'YTick',[1 2 3 4],'YTickLabel',...
    {'jan-march','april-june','jul-sep','oct-dec'});

set(axes1,'XTick',[1 2 3 4],'XTickLabel',...
     {'Toronto','New York','Haiti'});

 view(axes1,[152.30993247402 60.4]);
 
function perTimeDead = getPredTimeDeadForLocation(jsonFile)
    fname = jsonFile; 
    fid = fopen(fname); 
    raw = fread(fid,inf);
    str = char(raw'); 
    fclose(fid);
    val = jsondecode(str);

    %                     static             orchas               eno                less
%     perTimeDead = [[val(1).perTimeDead, val(5).perTimeDead, val(9).perTimeDead, val(13).perTimeDead],
%                    [val(2).perTimeDead, val(6).perTimeDead, val(10).perTimeDead, val(14).perTimeDead],
%                    [val(3).perTimeDead, val(7).perTimeDead, val(11).perTimeDead, val(15).perTimeDead],
%                    [val(4).perTimeDead, val(8).perTimeDead, val(12).perTimeDead, val(16).perTimeDead]];
               
    perTimeDead = [[val(1).perTimeDead, val(9).perTimeDead, val(13).perTimeDead],
                     [val(2).perTimeDead, val(10).perTimeDead, val(14).perTimeDead],
                     [val(3).perTimeDead, val(11).perTimeDead, val(15).perTimeDead],
                     [val(4).perTimeDead, val(12).perTimeDead, val(16).perTimeDead]];
end