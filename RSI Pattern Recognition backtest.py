

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import yfinance as yf



def smma(series,n):
    
    output=[series[0]]
    
    for i in range(1,len(series)):
        temp=output[-1]*(n-1)+series[i]
        output.append(temp/n)
        
    return output



def rsi(data,n=14):
    
    delta=data.diff().dropna()
    
    up=np.where(delta>0,delta,0)
    down=np.where(delta<0,-delta,0)
    
    rs=np.divide(smma(up,n),smma(down,n))
    
    output=100-100/(1+rs)
    
    return output[n-1:]



def signal_generation(df,method,n=14):
    
    df['rsi']=0.0
    df['rsi'][n:]=method(df['Close'],n=14)
    
    df['positions']=np.select([df['rsi']<30,df['rsi']>70], \
                              [1,-1],default=0)
    df['signals']=df['positions'].diff()
    
    return df[n:]



def plot(new,ticker):
    
    #
    fig=plt.figure(figsize=(10,10))
    ax=fig.add_subplot(211)
    
    new['Close'].plot(label=ticker)
    ax.plot(new.loc[new['signals']==1].index,
            new['Close'][new['signals']==1],
            label='LONG',lw=0,marker='^',c='g')
    ax.plot(new.loc[new['signals']==-1].index,
            new['Close'][new['signals']==-1],
            label='SHORT',lw=0,marker='v',c='r')

    
    plt.legend(loc='best')
    plt.grid(True)
    plt.title('Positions')
    plt.xlabel('Date')
    plt.ylabel('price')
    
    plt.show()
    
    
    bx=plt.figure(figsize=(10,10)).add_subplot(212,sharex=ax)
    new['rsi'].plot(label='relative strength index',c='#522e75')
    bx.fill_between(new.index,30,70,alpha=0.5,color='#f22f08')
    
    bx.text(new.index[-45],75,'overbought',color='#594346',size=12.5)
    bx.text(new.index[-45],25,'oversold',color='#594346',size=12.5)
    
    plt.xlabel('Date')
    plt.ylabel('value')
    plt.title('RSI')
    plt.legend(loc='best')
    plt.grid(True)
    plt.show()



def pattern_recognition(df,method,lag=14):
    
    df['rsi']=0.0
    df['rsi'][lag:]=method(df['Close'],lag)    
    
    
    period=25    
    
  
    delta=0.2
    
    
    head=1.1
    shoulder=1.1
    
    df['signals']=0
    df['cumsum']=0
    df['coordinates']=''
    
    
    entry_rsi=0.0
    counter=0
    exit_rsi=4
    exit_days=5
    
    
    for i in range(period+lag,len(df)):
        
        
        moveon=False
        top=0.0
        bottom=0.0
        
        
        if (df['cumsum'][i]==0) and  \
        (df['Close'][i]!=max(df['Close'][i-period:i])):
            
            j=df.index.get_loc(df['Close'][i-period:i].idxmax())
            
            
            if (np.abs(df['Close'][j]-df['Close'][i])>head*delta):
                bottom=df['Close'][i]
                moveon=True
            
            
            if moveon==True:
                moveon=False
                for k in range(j,i):    
                    if (np.abs(df['Close'][k]-bottom)<delta):
                        moveon=True
                        break
            
            
            if moveon==True:
                moveon=False
                for l in range(j,i-period+1,-1):
                    if (np.abs(df['Close'][l]-bottom)<delta):
                        moveon=True
                        break
                    
            
            if moveon==True:
                moveon=False        
                for m in range(i-period,l):
                    if (np.abs(df['Close'][m]-bottom)<delta):
                        moveon=True
                        break
            
            
            if moveon==True:
                moveon=False        
                n=df.index.get_loc(df['Close'][m:l].idxmax())
                if (df['Close'][n]-bottom>shoulder*delta) and \
                (df['Close'][j]-df['Close'][n]>shoulder*delta):
                    top=df['Close'][n]
                    moveon=True
                    
            if moveon==True:        
                for o in range(k,i):
                    if (np.abs(df['Close'][o]-top)<delta):
                        df.at[df.index[i],'signals']=-1
                        df.at[df.index[i],'coordinates']='%s,%s,%s,%s,%s,%s,%s'%(m,n,l,j,k,o,i)
                        df['cumsum']=df['signals'].cumsum()
                        entry_rsi=df['rsi'][i]
                        moveon=True
                        break
        
        
        if entry_rsi!=0 and moveon==False:
            counter+=1
            if (df['rsi'][i]-entry_rsi>exit_rsi) or \
            (counter>exit_days):
                df.at[df.index[i],'signals']=1
                df['cumsum']=df['signals'].cumsum()
                counter=0
                entry_rsi=0
            
    return df



def pattern_plot(new,ticker):
    
    
    a,b=list(new[new['signals']!=0].iloc[2:4].index)
    
  
    temp=list(map(int,new['coordinates'][a].split(',')))
    indexlist=list(map(lambda x:new.index[x],temp))
    
    
    c=new.index.get_loc(b)
    newbie=new[temp[0]-30:c+20]
    
    
    ax=plt.figure(figsize=(10,10)).add_subplot(211)
        
    newbie['Close'].plot(label=ticker)
    ax.plot(newbie['Close'][newbie['signals']==1],marker='^',markersize=12, \
            lw=0,c='g',label='LONG')
    ax.plot(newbie['Close'][newbie['signals']==-1],marker='v',markersize=12, \
            lw=0,c='r',label='SHORT')
    
    plt.legend(loc=0)
    plt.title('Positions')
    plt.xlabel('Date')
    plt.ylabel('price')
    plt.grid(True)
    plt.show()
    
    
    bx=plt.figure(figsize=(10,10)).add_subplot(212,sharex=ax)
    
    newbie['rsi'].plot(label='relative strength index',c='#f4ed71')
    
    
    bx.fill_between(newbie.index,30,70,alpha=0.6,label='overbought/oversold range',color='#000d29')
    bx.plot(newbie['rsi'][indexlist], \
            lw=3,alpha=0.7,marker='o', \
            markersize=6,c='#8d2f23',label='head-shoulder pattern')
    bx.plot(newbie['rsi'][newbie['signals']==1],marker='^',markersize=12, \
            lw=0,c='g',label='LONG')
    bx.plot(newbie['rsi'][newbie['signals']==-1],marker='v',markersize=12, \
            lw=0,c='r',label='SHORT')

    
    for i in [(1,'Shoulder'),(3,'Head'),(5,'Shoulder')]:
        plt.text(indexlist[i[0]], newbie['rsi'][indexlist[i[0]]]+2, \
             '%s'%i[1],fontsize=10,color='#e4ebf2', \
             horizontalalignment='center', \
            verticalalignment='center')
        
    plt.title('RSI')
    plt.legend(loc=1)
    plt.xlabel('Date')
    plt.ylabel('value')
    plt.grid(True)
    plt.show()
    
    



def main():
    
    ticker='TSLA'
    startdate='2016-01-01'
    enddate='2018-01-01'
    df=yf.download(ticker,start=startdate,end=enddate)
    new=signal_generation(df,rsi,n=14)

    plot(new,ticker)




if __name__ == '__main__':
    main()

