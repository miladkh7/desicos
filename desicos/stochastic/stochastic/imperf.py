"""
.. module:: imperf
   :platform: Unix, Windows

.. moduleauthor:: Pavel Schor <schor.pavel@gmail.com>


"""
import logging
import numpy as np
from scipy import fftpack
from scipy import interpolate
from stochastic.filWin import FilterWindows2D
from stochastic.strFact import StructurePattern
def nextpow2(n):
    m_f = np.log2(n)
    m_i = np.ceil(m_f)
    return int(m_i)

class Samples(object):

    """
        This class provides generation of new stochastic
        samples, which are based on already existing samples

    """

    def __init__(self):
        self.amplThreshold=5e-10
        self.fxRange=(0.0,0.1)
        self.fyRange=(0.0,0.1)
        self.indata=[]
        self.data=[]
        self.outdata=[]
        self.nSamples=0
        #self.fil=('hamming',(0.53836,-0.46164,0.53836,-0.46164) )#  ('trapezoid',(0.1,0.1))
        self.fil=('none',())
        self.strFacts=[StructurePattern()]

    def setFilter(self,name,args):
        self.fil=(name,args)

    def getCurrentFilterName(self):
        return self.fil[0]

    def getInputsCount(self):
        return len(self.indata)

    def getFilter(self):
        return self.winFilter
    def setAmplitudeThreshold(self,val):
        self.amplThreshold=val

    def setFreqRng(self,ax,rng):
        if ax == 'x':
            self.fxRange=rng
        if ax == 'y':
            self.fyRange=rng

    def setGeometry(self,RB,H,alpha):
        self.RB=RB
        self.H=H
        self.alpha=alpha
        self.RT=RB-H *( np.tan(alpha ) )
        self.strFacts[0].setGeometry(RB,H,alpha)

    def addSurfacePatternFactory(self,strFact):
        self.strFacts.append(strFact)
        self.strFacts[len(self.strFacts)-1].setGeometry(self.RB,self.H,self.alpha)

    def _getRperf(self,z):
        return (self.RB - z*np.tan(self.alpha))

    def addData(self,data,x,y):
        """    Use only this method to put 2D-data for futher processing.
            Data must lie on same regular grid as first data, you input.
            If not, this method will not add such input into buffer for
            futher processing
        """
        self.nSamples+=1
        if self.nSamples == 1:
            self.indata.append(data)
            (self.ny,self.nx)=data.shape
            self.ny=int(data.shape[0])
            self.x=x
            self.y=y
            self.lx=self.x[-1:][0]
            self.ly=self.y[-1:][0]


        else:
            if data.shape == self.indata[0].shape and x.all() == self.x.all() and y.all() == self.y.all():
                self.indata.append(data)
            else:
                logging.warning('Inconsistent data input!')
                logging.warning("Check data shape and X,Y sampling!")


    def cutFrequences(self):
        fxMaxPres=0.0
        fyMaxPres=0.0
        aMax=self.amplThreshold
        for i in range(self.sh.shape[0]):
            if np.max(self.sh[i,:]) > aMax:
                fxMaxPres=self.fx[i]
        for i in range(self.sh.shape[1]):
            if np.max(self.sh[:,i]) > aMax:
                fyMaxPres=self.fy[i]

        fxMin=fxMaxPres*self.fxRange[0]
        fxMax=fxMaxPres*self.fxRange[1]
        nFxMin=self.fx.searchsorted(fxMin)
        nFxCut=self.fx.searchsorted(fxMax)

        fyMin=fyMaxPres*self.fyRange[0]
        fyMax=fyMaxPres*self.fyRange[1]
        nFyMin=self.fx.searchsorted(fyMin)
        nFyCut=self.fy.searchsorted(fyMax)

        if nFxCut < 2:
            nFxCut=2
        if nFyCut < 2:
            nFyCut=2


        self.shCut=self.sh[0:nFxCut,0:nFyCut].copy()
        self.shCut[:,0:nFxMin]=0
        self.shCut[0:nFyMin,:]=0

        self.fxCut=self.fx[0:nFxCut]
        self.fyCut=self.fy[0:nFyCut]

        self.fxIn=np.linspace(0,self.fx[nFxCut-1],17)
        self.fyIn=np.linspace(0,self.fy[nFyCut-1],17)



    def compute(self):
        if len(self.indata) < 2:
            logging.warning("insufficient input count!")
            return
        FilterWindows2D.setInputArray(self.y,self.x)
        self.winFilter=FilterWindows2D.filters[self.fil[0]]( *self.fil[1]  )
        self.aveFunc=np.zeros(self.indata[0].shape)
        self.eW=np.zeros(self.indata[0].shape)

        for data in self.indata:
            self.aveFunc+=data/self.nSamples

        for i in range(len(self.indata)):
            self.data.append(self.indata[i]-self.aveFunc)
            self.eW+= (self.data[i]**2.0)/self.nSamples

        for i in range(len(self.data)):
            self.data[i]=self.data[i]*self.winFilter

        nFFT1 = 16*2**nextpow2(self.nx)
        nFFT2 = 16*2**nextpow2(self.ny)

        a1 = nFFT1/2
        a2 = nFFT2/2
        a2Mod = nFFT2/8/2

        self.a1=a1
        self.a2=a2
        self.sh=np.zeros((a1,a2))

        for data in self.data:
            z=np.fft.fft2(data,s=[nFFT1,nFFT2])
#            z=scipy.fftpack.fft2(data,shape=[nFFT1,nFFT2])
            trans= (np.abs(z)**2) / (nFFT1*nFFT2)
            self.sh+=trans[0:a1,0:a2]/self.nSamples
            self.trans=trans

        dfx=self.lx/(self.nx-1)
        dfy=self.ly/(self.ny-1)

        fx=2.*np.pi/dfx/nFFT1*np.linspace(0,a1-1,a1)
        fy=2.*np.pi/dfy/nFFT2*np.linspace(0,a2-1,a2)
        self.fx=fx
        self.fy=fy
        self.dfx=dfx
        self.dfy=dfy

        self.cutFrequences()
        FXin,FYin=np.meshgrid(self.fxIn,self.fyIn)
        FXcut,FYcut=np.meshgrid(self.fxCut,self.fyCut)
        self.FXcut=FXcut
        self.FYcut=FYcut

        fmod=interpolate.RectBivariateSpline(self.fxCut,self.fyCut,self.shCut,kx=1,ky=1 )
        self.shMod=fmod(self.fxIn,self.fyIn)

        intSh=0.0
        for i in range(0,len(self.fxIn)-1):
            for j in range(0,len(self.fyIn)-1):
                intSh=intSh+self.shMod[i][j]*self.fxIn[1]*self.fyIn[1]
        if intSh >0.0:
            self.bruch=self.shMod/(4.0*intSh)
        else:
            self.bruch=self.shMod



    def getNewSample(self):
        x=self.x
        y=self.y
        eW=self.eW
        bruch=self.bruch
        fxIn=self.fxIn
        fyIn=self.fyIn
        res=np.zeros((self.ny,self.nx))
        phi1=np.zeros(self.shMod.shape)
        phi2=np.zeros(self.shMod.shape)
        sqrt2=np.sqrt(2.)
#        bruch=np.loadtxt('stochastic/bruch',delimiter=',')

        for i in range(1,self.shMod.shape[0]):
            for j in range(1,self.shMod.shape[1]):
                phi1[i][j]=2*np.pi*np.random.rand()
                phi2[i][j]=2*np.pi*np.random.rand()
#        phi1=np.loadtxt('stochastic/phi1',delimiter=',')
#        phi2=np.loadtxt('stochastic/phi2',delimiter=',')

        dfx=fxIn[1].copy()
        dfy=fyIn[1].copy()

        for iy in range(0,self.ny):
            for ix in range(0,self.nx):
                for n1 in range(1,self.shMod.shape[0]):
                    for n2 in range(1,self.shMod.shape[1]):
                        A1=np.sqrt(2.0*eW[iy][ix]*bruch[n1][n2]*dfx*dfy)

                        res[iy][ix]+=sqrt2*(A1*np.cos(fxIn[n1]*x[ix]+fyIn[n2]*y[iy]+phi1[n1][n2])+ \
                                        A1*np.cos(fxIn[n1]*x[ix]-fyIn[n2]*y[iy]+phi2[n1][n2]))
        res+=self.aveFunc
        self._tmp_res=res.copy()
        self._tmp_pat=np.zeros(self._tmp_res.shape)
        for strFact in self.strFacts:
            strFact.connectOutputArray(res)
            pat=strFact.getPattern()

            res+=pat
            self._tmp_pat+=pat

        return res


