import wx

import winsound

class MyTimer(wx.Frame):
     def __init__(self):
          wx.Frame.__init__(self, None, wx.ID_ANY,
                            style=wx.DEFAULT_FRAME_STYLE ^ wx.RESIZE_BORDER)
          panel = wx.Panel(self)

          mainSizer = wx.BoxSizer(wx.VERTICAL)
          inputSizer = wx.BoxSizer(wx.HORIZONTAL)

          self.minutesPassed = 1.0
          self.progress = wx.Gauge(panel, wx.ID_ANY, 100, size=(1000, 40))
          self.status = wx.StaticText(panel, wx.ID_ANY, '')

          font = wx.Font(30, wx.FONTFAMILY_MODERN, 
                         wx.FONTSTYLE_NORMAL, wx.FONTWEIGHT_BOLD)
          self.status.SetFont(font)
         
          self.start = wx.Button(panel, wx.ID_ANY, 'Start')
          self.stop  = wx.Button(panel, wx.ID_ANY, 'Stop')
          self.reset = wx.Button(panel, wx.ID_ANY, 'Reset')
          self.reset.Disable()
          self.timer = wx.Timer(self)

          mainSizer.Add(self.progress, flag=wx.ALIGN_CENTER | wx.ALL ^ wx.BOTTOM,
                        border=10)
          mainSizer.Add(self.status, flag=wx.ALIGN_LEFT | wx.ALL, 
                        border=10)
          mainSizer.Add(inputSizer, flag=wx.ALIGN_CENTER | wx.BOTTOM, 
                        border=10)
          
          inputSizer.Add(self.start, flag=wx.ALIGN_CENTER)
          inputSizer.Add(self.stop, flag=wx.ALIGN_CENTER)
          inputSizer.Add(self.reset, flag=wx.ALIGN_CENTER)
          
          
          self.Bind(wx.EVT_BUTTON, self.OnStart, self.start)
          self.Bind(wx.EVT_BUTTON, self.OnStop, self.stop)
          self.Bind(wx.EVT_TIMER, self.OnTimer, self.timer)
          self.Bind(wx.EVT_BUTTON, self.OnReset, self.reset)

          panel.SetSizer(mainSizer)
          mainSizer.Fit(self)

     def OnStart(self, event):
          self.countdown = self.time - 1.0
          self.start.Disable()
          self.stop.Enable()
          self.reset.Enable()
          
          self.timer.Start(1000.0)

          self.stopped = False

     def OnStop(self, event):
          if not self.stopped:
               self.stopped = True
               self.stop.SetLabel('Restart')
               self.timer.Stop()
               
          else:
               self.stopped = False
               self.stop.SetLabel('Stop')
               self.timer.Start(1000.)
          
     def OnReset(self, event):
          self.progress.SetValue(0.0)
          self.minutesPassed = 1.0
          self.start.Enable()
          self.timer.Stop()


     def OnTimer(self, event):
          print self.countdown, self.buffer_time
          if self.countdown >= self.warning_time:
               self.progress.SetValue(self.minutesPassed * (100. / self.time))
               self.status.SetLabel('%1.2f minutes remaining.' % (self.countdown/60.))              
               self.minutesPassed += 1.
               self.countdown -= 1.

          elif self.countdown < self.warning_time and self.countdown >= 60.0:
               self.progress.SetValue(self.minutesPassed * (100. / self.time))
               self.status.SetLabel('%1.2f minutes remaining.' % (self.countdown/60.))
               self.status.SetBackgroundColour('yellow')
               self.minutesPassed += 1.
               self.countdown -= 1.
     
          elif self.countdown <  60.0 and self.countdown >= 0:
               self.progress.SetValue(self.minutesPassed * (100. / self.time))
               self.status.SetLabel('%1.2f minutes remaining. \nTime is running out. Start uploading now!' % (self.countdown/60.))
               self.status.SetBackgroundColour('red')
               self.minutesPassed += 1.
               self.countdown -= 1.

          elif self.countdown < -self.buffer_time:
               self.timer.Stop()
               self.Destroy()
               
          # this is the buffer step
          else:
               self.progress.SetValue(self.minutesPassed * (100. / self.time))
               self.status.SetLabel('The exam is over!')
               self.status.SetBackgroundColour('red')
               winsound.PlaySound('ding.wav',winsound.SND_FILENAME)
               self.countdown -= 1.


class MyApp(wx.App):

     def OnInit(self):
         self.frame = MyTimer()
         self.SetTopWindow(self.frame)
         self.frame.Show()
         return True

     def set_time(self, time):
          ''' this is the time to run the timer'''
          self.frame.time = time

     def set_warning_time(self, warning_time=2):
          ''' when this time is left the time turns orange'''
          self.frame.warning_time = warning_time

     def set_buffer_time(self, buffer_time=1):
          '''set extra time for uploads'''
          self.frame.buffer_time = buffer_time

     def run(self):
          self.frame.stopped = False
          self.frame.countdown = self.frame.time - 1.0
          self.frame.timer.Start(1000.0)

if __name__ == '__main__':
     app = MyApp(False)
     app.MainLoop()


